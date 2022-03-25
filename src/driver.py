import time
import platform
import requests
from typing import *
from loguru import logger

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from .config import Config
from .yidun import yidun


class Chrome:
    def __init__(self) -> None:
        """初始化并建立一个chromedriver"""
        self.Config = Config()
        self.yidun = yidun()

        if platform.system().lower() == "linux":
            chromium_path = "./source/chromedriver"
        else:
            chromium_path = "./source/chromedriver.exe"
        logger.debug(f"检测系统为: {platform.system().lower()}, 将尝试在source目录下寻找对应driver")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        service = Service(chromium_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

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

    def get(self, url: str) -> bool:
        """让driver访问打卡网页的地址

        Args:
            url (str): 打卡网页的地址

        Raises:
            e: 可能的出错原因
        """
        try:
            logger.info(f"正在尝试访问网页: {url} ……")
            self.driver.get(url)
            time.sleep(2)
        except Exception as e:
            logger.error(f"访问网页 {url} 失败!")
            raise e

    def input_passwd(self) -> None:
        """自动填入账号密码登录, 如果config中不存在则自动询问"""
        logger.info("输入账号密码中……")
        user = self.Config.get_user()
        login_windows = self.driver.find_element(By.XPATH, '//*[@id="zh"]')
        passwd_windows = self.driver.find_element(By.XPATH, '//*[@id="passw"]')
        self.login_button = self.driver.find_element(
            By.XPATH,
            "/html/body/app-root/app-login/div[2]/div[2]/form/div[5]/div/button",
        )
        login_windows.send_keys(user[0])
        passwd_windows.send_keys(user[1])

        time.sleep(2)

    def input_data(self) -> bool:
        """自动填入温度以及当前所在地

        Returns:
            bool: 是否成功
        """

        logger.info("正在填入各项信息……")
        logger.info("正在填入温度……")
        self.input_temp('//*[@id="cjtw"]', '//*[@id="twyjcrq"]', True)
        self.input_temp('//*[@id="wujtw"]', '//*[@id="twejcrq"]', False)
        self.input_temp('//*[@id="wajtw"]', '//*[@id="twsjcrq"]', False)

        # 如果当前所在地为`在家`则没法使用
        try:
            self.input_living()
        except Exception as e:
            logger.info("检查到目前所在地并非为`在外地`, 不需填写详细地址")
            logger.debug(f"跳过原因:{e}")

        self.driver.find_element(By.XPATH, '//*[@id="10000"]').click()
        logger.info("最后检查时间: 5s\n 5s后提交")
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="tj"]').click()
        return True

    def input_living(self) -> None:
        """自动填入当前所在地"""

        def __print(data: Select) -> str:
            """格式化打印地址以供选择

            Args:
                data (Select): select

            Returns:
                str: 用户选择的地点如广州市、番禺区等
            """
            t1 = [
                f"{x}.{y.text}" for x, y in enumerate(data.options) if (x + 1) % 5 == 1
            ]
            t2 = [
                f"{x}.{y.text}" for x, y in enumerate(data.options) if (x + 1) % 5 == 2
            ]
            t3 = [
                f"{x}.{y.text}" for x, y in enumerate(data.options) if (x + 1) % 5 == 3
            ]
            t4 = [
                f"{x}.{y.text}" for x, y in enumerate(data.options) if (x + 1) % 5 == 4
            ]
            t5 = [
                f"{x}.{y.text}" for x, y in enumerate(data.options) if (x + 1) % 5 == 0
            ]
            t = (
                f"{f'  '.join(t1)}\n"
                f"{f'  '.join(t2)}\n"
                f"{f'  '.join(t3)}\n"
                f"{f'  '.join(t4)}\n"
                f"{f'  '.join(t5)}\n"
            )
            ans = input(t + "请输入你当前所在地,若无子地点请输入0,即请选择(仅需首次运行输入一次)")
            return data.options[int(ans)].text

        living = self.Config.get_living()
        if not living:
            P = C = D = None
            save = True
        else:
            P, C, D = living[0], living[1], living[2]
            save = False

        province = Select(
            self.driver.find_element(By.XPATH, '//*[@id="selectProvince"]')
        )
        if not P:
            P = __print(province)
        province.select_by_visible_text(P)

        city = Select(self.driver.find_element(By.XPATH, '//*[@id="selectCity"]'))
        if not C:
            C = __print(city)
        city.select_by_visible_text(C)

        district = Select(
            self.driver.find_element(By.XPATH, '//*[@id="selectDistrict"]')
        )
        if not D:
            D = __print(district)
        district.select_by_visible_text(D)
        if save:
            self.Config.set_living(P, C, D)
        return [P, C, D]

    def input_temp(self, temp_xpath: str, date_xpath: str, today: bool) -> None:
        """自动填入温度

        可恶！一天三检！我是百变温度怪咋的

        Args:
            temp_xpath (str): 温度一栏的xpath
            date_xpath (str): 日期一栏的xpath
            today (bool): 是否将日期选择为今天, 否则为昨天(按要求目前仅早上为今天 中午以及晚上温度皆选为昨天)
        """
        temperture = self.driver.find_element(
            By.XPATH,
            temp_xpath,
        )
        temperture.clear()
        temperture.send_keys(self.Config.random_temp())

        date = self.driver.find_element(By.XPATH, date_xpath)
        ActionChains(self.driver).click(date).perform()
        if not today:
            date.send_keys(Keys.LEFT)
        date.send_keys(Keys.ENTER)

    def save_img(self) -> None:
        """保存验证码图片用作计算"""
        target_link = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "yidun_bg-img"))
        ).get_attribute("src")
        template_link = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "yidun_jigsaw"))
        ).get_attribute("src")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
        }

        with open("./images/target.jpg", "wb") as f:
            f.write(requests.get(target_link, headers=headers).content)

        with open("./images/template.png", "wb") as f:
            f.write(requests.get(template_link, headers=headers).content)

    def crack(self) -> bool:
        """一条龙验证？

        Returns:
            bool: 是否成功通过滑条验证
        """
        self.save_img()
        tracks = self.yidun.crack(
            target_img="./images/target.jpg", template_img="./images/template.png"
        )
        self.move_to_gap(tracks=tracks)
        return self.Slider_Success()

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

    def Slider_Success(self) -> bool:
        """确认滑条验证是否成功, 如果失败过多, 需要点击重试则点击并传回False

        Args:
            fail (int): 失败次数, 首次调用跳过验证(因为自己代码的原因, 第一次还没执行crack方法)

        Returns:
            bool: 滑条验证是否通过
        """
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
            logger.info("验证还就内个成昆!帅的嘛不谈")
            return True
        else:
            logger.info(
                "失败了捏,你可选的解决方案:\n1. [ 不推荐 ] 等待这该死的程序自动重试并无所事事的看着\n2. [ 推荐 ] 即刻关注`嘉然今天吃什么`来迅速度过无聊的重试时间: https://space.bilibili.com/672328094"
            )

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
            try:
                ele2 = self.driver.find_element(
                    By.XPATH,
                    "/html/body/app-root/app-index/div/div[1]/app-cantwrite/section/section/div/div/div/div/div/div[2]/label",
                )
                if ele2.text == "距离您上一次健康申报间隔还不足6小时，请稍后再试":
                    logger.info("距离您上一次健康申报间隔还不足6小时，请稍后再试…")
                    return True
            except NoSuchElementException:
                return False
        except Exception as e:
            logger.debug(f"判断打卡状态发生错误({e}), 无法判断当前是否打卡了, 尝试继续打卡")
            return False

    def close_driver(self) -> None:
        self.driver.close()
        self.driver.quit()
