import sys
import cv2
import time
import json
import random
import requests
import numpy as np
from typing import *
from PIL import Image
from io import BytesIO

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import soraha_utils


logger = soraha_utils.set_logger(level="DEBUG")


class Chrome:
    def __init__(
        self,
        chromium_path: str = "./source/chromedriver.exe",
        proxy_server: Optional[str] = None,
        wait_timeout: int = 20,
    ) -> None:
        """初始化并建立一个chromedriver

        Args:
            chromium_path (str, optional): chromdriver路径. Defaults to "./source/chromedriver.exe".
            proxy_server (Optional[str], optional): 代理服务器(可选),格式参考: `127.0.0.1:8080`. Defaults to None.
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
        )
        if proxy_server:
            chrome_options.add_argument(f"--proxy-server={proxy_server}")

        service = Service(chromium_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.wait = WebDriverWait(self.driver, wait_timeout)

        # 将navigator.webdriver设为undefined
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })"""
            },
        )
        logger.info("成功开启chromedriver!")
        self.load_config()

    def load_config(self) -> None:
        logger.info("正在加载配置……")
        try:
            with open("./config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
                if not self.config["temperture"]:
                    self.config["temperture"] = round(random.uniform(36.1, 36.9), 1)
                    logger.debug(f"即将填入的温度为: {self.config['temperture']}")
            logger.info("配置加载成功!")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error("配置config.json未正确配置,请确保按说明填写并且在同文件夹下!")

        except Exception as e:
            logger.error(f"读取配置文件时发生未知错误!: {e}")
            time.sleep(3)
            raise e

    def get(self, url: str) -> bool:
        """访问打卡网站

        Args:
            url (str, optional): 打卡网页的地址. Defaults to "https://stuhealth.jnu.edu.cn/#/login".

        Returns:
            bool: False则为错误,否则返回True
        """
        try:
            logger.info(f"正在尝试访问网页: {url} ……")
            self.driver.get(url)
            time.sleep(2)
        except Exception as e:
            logger.error(f"访问网页 {url} 出现错误: {e}")
            return False
        return True

    def reflash_temp(self):
        logger.info("失败次数超过三次,尝试刷新一次验证码")
        ActionChains(self.driver).move_to_element(
            self.driver.find_element(By.XPATH, '//*[@id="captcha"]/div/div[2]/div[3]')
        ).perform()
        time.sleep(1)
        self.driver.find_element(
            By.XPATH, '//*[@id="captcha"]/div/div[1]/div/div[3]/div/button'
        ).click()

    def move_to_gap(self, tracks):
        logger.info("正在尝试验证……")
        logger.debug(f"tracks: {tracks}")
        slider = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "yidun_slider"))
        )
        ActionChains(self.driver).click_and_hold(slider).perform()
        while tracks:
            x = tracks.pop(0)
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.05)
        ActionChains(self.driver).release().perform()

    def Slider_Success(self, fail: int) -> bool:
        """确认滑条验证是否成功, 如果失败过多, 需要点击重试则点击并传回False

        Args:
            fail (int): 失败次数, 首次调用跳过验证(因为自己代码的原因, 第一次还没执行crack方法)

        Returns:
            bool: 滑条验证是否通过
        """
        if fail == 0:
            return
        time.sleep(1)
        logger.info("正在确认验证是否成功……")
        # 滑条, 通过判断长度是否回到了初始的 2 来决定是否成功验证
        slide = self.driver.find_element(
            By.CLASS_NAME,
            "yidun_slide_indicator",
        )
        try:
            # 查找文字, 是否存在 失败过多，点此重试 的字样
            ele = self.driver.find_element(
                By.XPATH, '//*[@id="captcha"]/div/div[2]/div[3]/span[2]'
            )
            if ele.text.strip() == "失败过多，点此重试":
                # 请关注嘉然今天吃什么捏~
                logger.info("失败过多了……正在点击重试,肯定是因为你没有关注嘉然今天吃什么!")
                ele = self.driver.find_element(By.CLASS_NAME, "yidun_tips")
                ActionChains(self.driver).move_to_element(ele).click(ele).perform()
                return False
        except:
            pass
        if slide.rect["width"] > 2:
            logger.info("验证还就内个成昆怎么说?")
            return True
        else:
            logger.info(
                "失败了捏,你可选的解决方案:\n1. [ 不推荐 ]等待这该死的程序自动重试并无所事事的看着\n2. [ 推荐 ]即刻关注`嘉然今天吃什么`来迅速度过无聊的重试时间: https://space.bilibili.com/672328094"
            )

    def input_data(self) -> None:
        logger.info("正在填入各项信息……")
        temperture = self.driver.find_element(By.XPATH, '//*[@id="temperature"]')
        temperture.clear()
        temperture.send_keys(str(self.config["temperture"]))
        # 如果当前所在地为`在家`则没法使用
        try:
            province = Select(
                self.driver.find_element(By.XPATH, '//*[@id="selectProvince"]')
            )
            province.select_by_visible_text(self.config["province"])
            city = Select(self.driver.find_element(By.XPATH, '//*[@id="selectCity"]'))
            city.select_by_visible_text(self.config["city"])
            district = Select(
                self.driver.find_element(By.XPATH, '//*[@id="selectDistrict"]')
            )
            district.select_by_visible_text(self.config["district"])
        except:
            logger.info("检查到目前所在地并非为`在外地`, 不需填写详细地址")
        self.driver.find_element(By.XPATH, '//*[@id="10000"]').click()
        logger.info("最后检查时间: 5s\n 5s后提交")
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="tj"]').click()

    def input_passwd(self) -> None:
        logger.info("输入账号密码中……")
        login_windows = self.driver.find_element(By.XPATH, '//*[@id="zh"]')
        passwd_windows = self.driver.find_element(By.XPATH, '//*[@id="passw"]')
        self.login_button = self.driver.find_element(
            By.XPATH,
            "/html/body/app-root/app-login/div[2]/div[2]/form/div[5]/div/button",
        )
        login_windows.send_keys(self.config["user_name"])
        passwd_windows.send_keys(self.config["passwd"])

    def is_clock_in(self) -> bool:
        try:
            ele = self.driver.find_element(
                By.XPATH,
                "/html/body/app-root/app-index/div/div[1]/app-complete/section/section/div/div/div/div/div/div[2]/label",
            )
            if ele.text == "您已完成今天的健康状态申报":
                logger.info("您已完成今天的健康状态申报!")
                return True
        except NoSuchElementException:
            return False


class CrackSlider(Chrome):
    def __init__(
        self,
        chromium_path: str = "./source/chromedriver.exe",
        url: str = "https://stuhealth.jnu.edu.cn/#/login",
        proxy_server: Optional[str] = None,
    ) -> None:
        """创建Chrome浏览器并初始化一个网易易盾破解类
        使用该类请直接调用crack方法, 该方法包含了从获取图片->计算验证码->滑动滑条并松开的动作
        ```
        cs = CrackSlider(……)
        cs.crack(xp)
        ```

        Args:
            chromium_path (str, optional): chromedriver路径. Defaults to "./source/chromedriver.exe".
            url (str, optional): 需要访问的网址. Defaults to "https://stuhealth.jnu.edu.cn/#/login".
            proxy_server (Optional[str], optional): 代理服务器. Defaults to None.
        """
        super().__init__(chromium_path, proxy_server)
        self.proxy_dict = {
            "http": f"http://{proxy_server}" if proxy_server else None,
            "https": f"http://{proxy_server}" if proxy_server else None,
        }
        super().get(url)

    def crack(self, xp: int = 320) -> None:
        """易盾破解一条龙(?)

        Args:
            xp (int, optional): 验证码的大小,易盾默认为320,应该不需要改变. Defaults to 320.

        Returns:
            None: 该方法不提供成功与否的结果, 想确定请调用父级的Slider_Success方法
        """
        zoom = self.__get_img(xp)
        logger.info("正在尝试计算图形验证码……")
        distance = self.__match()
        track = self.__get_tracks(
            (distance + 7) * zoom,
        )
        self.move_to_gap(track)

    def __get_img(self, xp: int) -> int:
        def __open(
            target_link: str,
            proxy_dict: dict,
            headers: dict = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
            },
        ) -> Image:
            try:
                logger.info(f"正在尝试访问图片: {target_link} ……")
                return Image.open(
                    BytesIO(
                        requests.get(
                            target_link, proxies=proxy_dict, headers=headers
                        ).content
                    )
                )
            except Exception as e:
                logger.error(f"访问图片 {target_link} 失败: {e}")
                time.sleep(3)
                raise e

        self.target_link = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "yidun_bg-img"))
        ).get_attribute("src")
        self.template_link = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "yidun_jigsaw"))
        ).get_attribute("src")
        target_img = __open(self.target_link, self.proxy_dict)
        template_img = __open(self.template_link, self.proxy_dict)
        logger.info("正在保存图片至`./images/`下")
        target_img.save("./images/target.jpg")
        template_img.save("./images/template.png")
        size_loc = target_img.size
        zoom = xp / int(size_loc[0])
        return zoom

    def __change_size(self, file):
        image = cv2.imread(file, 1)
        img = cv2.medianBlur(image, 5)
        b = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)
        binary_image = b[1]
        binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
        x, y = binary_image.shape
        edges_x = []
        edges_y = []
        for i in range(x):
            for j in range(y):
                if binary_image[i][j] == 255:
                    edges_x.append(i)
                    edges_y.append(j)

        left = min(edges_x)
        right = max(edges_x)
        width = right - left
        bottom = min(edges_y)
        top = max(edges_y)
        height = top - bottom
        pre1_picture = image[left : left + width, bottom : bottom + height]
        return pre1_picture

    def __match(self) -> int:
        img_gray = cv2.imread("./images/target.jpg", 0)
        img_rgb = self.__change_size("./images/template.png")
        template = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        run = 1

        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            if threshold < 0:
                print("Error")
                return None
            loc = np.where(res >= threshold)
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]

    def __get_tracks(
        self,
        distance: int,
        seconds: int = random.randint(2, 4),
        ease_func: Optional[Callable] = lambda x: 1 - pow(1 - x, 4),
    ):
        distance += 20
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            offset = round(ease_func(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])
        return tracks


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--chrome-path":
        chromium = args[1]
    else:
        chromium = None

    logger.info("正在尝试启动chromedriver")
    logger.debug(f"指定的chromedriver路径为: {chromium}")

    if chromium:
        cs = CrackSlider(chromium)
    else:
        cs = CrackSlider()

    cs.input_passwd()

    fail = 0
    while not cs.Slider_Success(fail):
        # if fail == 3:
        #     cs.reflash_temp()
        #     fail = 0
        cs.crack()
        fail += 1

    ele = cs.driver.find_element(
        By.XPATH, "/html/body/app-root/app-login/div[2]/div[2]/form/div[5]/div/button"
    )
    ActionChains(cs.driver).move_to_element(ele).click(ele).perform()
    time.sleep(1)

    if not cs.is_clock_in():
        time.sleep(4)
        cs.input_data()
        logger.info("提交成功!")

    logger.info("三秒后即将退出程序")
    time.sleep(3)
