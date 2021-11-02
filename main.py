import sys
import time

import json
import random
import requests
import cv2
import numpy as np
from soraha_utils import *

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select

from exception import *


class sel:
    def __init__(
        self, chromium_path: str = "./chromedriver.exe", config_path="./config.json"
    ) -> None:
        self.chrome = chromium_path
        self.config_path = config_path
        try:
            self.driver = webdriver.Chrome(self.chrome)
        except:
            self._raise(msg="请确保传入正确的chromedirver路径/根目录存在chromdriver", exit_code=0)
        self.driver.get("https://stuhealth.jnu.edu.cn/#/login")
        self.load_config()

    def _raise(
        self, exception: Exception = None, msg: str = "发生错误", exit_code: int = 0
    ):
        if exception:
            logger.warning(msg)
            raise exception
        logger.warning(msg)
        time.sleep(3)
        sys.exit(exit_code)

    def input_passwd(self) -> None:
        login_windows = self.driver.find_element_by_xpath('//*[@id="zh"]')
        passwd_windows = self.driver.find_element_by_xpath('//*[@id="passw"]')
        self.login_button = self.driver.find_element_by_xpath(
            "/html/body/app-root/app-login/div[2]/div[2]/form/div[5]/div/button"
        )
        login_windows.send_keys(self.config["user_name"])
        passwd_windows.send_keys(self.config["passwd"])

    def load_config(self) -> None:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                if not self.config["temperture"]:
                    self.config["temperture"] = round(random.uniform(36.1, 36.9), 1)
        except (json.JSONDecodeError, FileNotFoundError):
            self._raise(msg="配置config.json未正确配置,请确保按说明填写并且在同文件夹下\n 三秒后将退出")
        except Exception as e:
            self._raise(msg=str(e))

    def match_temp(self):
        def match(target: str, template: str) -> int:
            img_rgb = cv2.imread(target)
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(template, 0)
            run = 1
            w, h = template.shape[::-1]
            print(w, h)
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            run = 1

            # 使用二分法查找阈值的精确值
            L = 0
            R = 1
            while run < 20:
                run += 1
                threshold = (R + L) / 2
                print(threshold)
                if threshold < 0:
                    print("Error")
                    return None
                loc = np.where(res >= threshold)
                print(len(loc[1]))
                if len(loc[1]) > 1:
                    L += (R - L) / 2
                elif len(loc[1]) == 1:
                    print("目标区域起点x坐标为：%d" % loc[1][0])
                    break
                elif len(loc[1]) < 1:
                    R -= (R - L) / 2
            return loc[1][0]

        def get_img() -> None:
            """下载图片

            Args:
                dv (webdriver.Chrome): selenium打开的chromedrive

            Returns:
                list[bytes]: 两张图片的bytes
            """

            img_url = []
            time.sleep(2.5)
            element = self.driver.find_element_by_xpath(
                '//*[@id="captcha"]/div/div[1]/div/div[1]/img[1]'
            )
            img_url.append(element.get_attribute("src"))

            element = self.driver.find_element_by_xpath(
                '//*[@id="captcha"]/div/div[1]/div/div[1]/img[2]'
            )
            img_url.append(element.get_attribute("src"))

            sync_uio.save_file(
                type="url_image", url=img_url[0], save_path="./target.png"
            )
            sync_uio.save_file(
                type="url_image", url=img_url[1], save_path="./template.png"
            )

        get_img()
        drag_ele = self.driver.find_element_by_xpath(
            '//*[@id="captcha"]/div/div[2]/div[2]'
        )
        ActionChains(self.driver).click_and_hold(drag_ele).perform()
        ActionChains(self.driver).move_by_offset(
            match("./target.png", "./template.png") + 10.0, 0
        ).perform()
        ActionChains(self.driver).pause(0.5).release().perform()
        time.sleep(1)
        self.login_button.click()
        time.sleep(3)
        try:
            self.driver.find_element_by_xpath(
                "/html/body/app-root/app-index/div/div[1]/app-home/section/section/div/div/div/div/div/h2"
            )
            return True
        except:
            return False

    def reflash_temp(self):
        ActionChains(self.driver).move_to_element(
            self.driver.find_element_by_xpath('//*[@id="captcha"]/div/div[2]/div[3]')
        ).perform()
        time.sleep(1)
        self.driver.find_element_by_xpath(
            '//*[@id="captcha"]/div/div[1]/div/div[3]/div/button'
        ).click()

    def input_data(self) -> None:
        temperture = self.driver.find_element_by_xpath('//*[@id="temperature"]')
        temperture.clear()
        temperture.send_keys(str(self.config["temperture"]))
        province = Select(
            self.driver.find_element_by_xpath('//*[@id="selectProvince"]')
        )
        province.select_by_visible_text(self.config["province"])
        city = Select(self.driver.find_element_by_xpath('//*[@id="selectCity"]'))
        city.select_by_visible_text(self.config["city"])
        district = Select(
            self.driver.find_element_by_xpath('//*[@id="selectDistrict"]')
        )
        district.select_by_visible_text(self.config["district"])
        self.driver.find_element_by_xpath('//*[@id="10000"]').click()
        logger.info("最后检查时间: 5s\n 5s后提交")
        time.sleep(5)
        self.driver.find_element_by_xpath('//*[@id="tj"]').click()


def main():
    dv = sel()
    dv.input_passwd()

    while not dv.match_temp():
        dv.reflash_temp()

    dv.input_data()


if __name__ == "__main__":
    main()
