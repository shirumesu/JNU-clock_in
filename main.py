import sys
import time

import json
import random
import requests
import aircv as ac
from loguru import logger

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select

from exception import *


def load_json(json_path: str = "./config.json") -> dict:
    """加载json文件,获取用户的信息用于输入

    Args:
        json_path (str): json文件的地址, 默认为'./config.json'

    Returns:
        info (dict): 用户的信息,json解析的文件
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            info = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.warning("配置config.json未正确配置,请确保按说明填写并且在同文件夹下\n 三秒后将退出")
        time.sleep(3)
        sys.exit(0)
    except:
        logger.warning("发生未知错误,三秒后退出")
        time.sleep(3)
        sys.exit(0)

    return info


def main():
    try:
        dv = webdriver.Chrome("./chromedriver.exe")
    except:
        logger.warning("请确保根目录拥有chromedriver")
        time.sleep(3)
        sys.exit(0)

    # 访问 https://stuhealth.jnu.edu.cn/#/login
    dv.get("https://stuhealth.jnu.edu.cn/#/login")

    # 输入账号密码
    login_windows = dv.find_element_by_xpath('//*[@id="zh"]')
    passwd_windows = dv.find_element_by_xpath('//*[@id="passw"]')
    login_button = dv.find_element_by_xpath(
        "/html/body/app-root/app-login/div[2]/div[2]/form/div[5]/div/button"
    )
    login_windows.send_keys(info["user_name"])
    passwd_windows.send_keys(info["passwd"])

    # 滑条验证码部分
    find_temp = False
    while not find_temp:
        get_img(dv)
        try:
            x = parser_photo()
        except Temp_not_found_Error:
            ActionChains(dv).move_to_element(
                dv.find_element_by_xpath('//*[@id="captcha"]/div/div[2]/div[3]')
            ).perform()
            time.sleep(1)
            dv.find_element_by_xpath(
                '//*[@id="captcha"]/div/div[1]/div/div[3]/div/button'
            ).click()
            continue
        drag_ele = dv.find_element_by_xpath('//*[@id="captcha"]/div/div[2]/div[2]')
        ActionChains(dv).click_and_hold(drag_ele).perform()
        ActionChains(dv).move_by_offset(x + 10, 0).perform()
        ActionChains(dv).pause(0.5).release().perform()
        time.sleep(1)
        login_button.click()
        try:
            time.sleep(3)
            check_text = dv.find_element_by_xpath(
                "/html/body/app-root/app-index/div/div[1]/app-home/section/section/div/div/div/div/div/h2"
            )
            find_temp = True
        except:
            continue

    # 输入数据部分
    temperture = dv.find_element_by_xpath('//*[@id="temperature"]')
    temperture.clear()
    temperture.send_keys(info["temperture"] if info["temperture"] else str(gen_temp()))
    province = Select(dv.find_element_by_xpath('//*[@id="selectProvince"]'))
    province.select_by_visible_text(info["province"])
    city = Select(dv.find_element_by_xpath('//*[@id="selectCity"]'))
    city.select_by_visible_text(info["city"])
    district = Select(dv.find_element_by_xpath('//*[@id="selectDistrict"]'))
    district.select_by_visible_text(info["district"])
    dv.find_element_by_xpath('//*[@id="10000"]').click()
    logger.info("最后检查时间: 5s\n 5s后提交")
    time.sleep(5)
    dv.find_element_by_xpath('//*[@id="tj"]').click()

    return input("按任意键退出")


def gen_temp() -> int:
    return round(random.uniform(36.1, 36.9), 1)


def get_img(dv: webdriver.Chrome) -> None:
    """下载图片

    Args:
        dv (webdriver.Chrome): selenium打开的chromedrive

    Returns:
        list[bytes]: 两张图片的bytes
    """

    img_url = []
    time.sleep(2.5)
    element = dv.find_element_by_xpath(
        '//*[@id="captcha"]/div/div[1]/div/div[1]/img[1]'
    )
    img_url.append(element.get_attribute("src"))

    element = dv.find_element_by_xpath(
        '//*[@id="captcha"]/div/div[1]/div/div[1]/img[2]'
    )
    img_url.append(element.get_attribute("src"))

    return down_img(img_url)


def down_img(url_list: list[str]) -> None:
    """分别下载验证码的图片背景与拼图板块图片

    Args:
        url_list (list[str]): 在selenium获取的两张图片的链接

    Raises:
        FileNotFoundError: 没有找到图片时抛出错误
    """
    if not url_list or None in url_list:
        logger.warning("没有找到图片!")
        time.sleep(3)
        raise FileNotFoundError

    try:
        [save_img(requests.get(x), y) for x, y in zip(url_list, ["target", "tempr"])]
    except ValueError:
        logger.warning("程序错误：请关闭系统代理,五秒后退出")
        time.sleep(5)
        sys.exit(0)


def save_img(req: requests.get, ph_name: str) -> None:
    """将图片保存

    Args:
        req (requests.get): request.get，获取content
        ph_name (str): 保存的文件名字
    """
    with open(f"./{ph_name}.jpg", "wb") as f:
        f.write(req.content)


def parser_photo() -> int:
    """解析验证码,获取拼图在背景的x值

    Attr:
        target: 背景
        template: 拼图板块

    Returns:
        int: 缺失的板块在背景的x值
    """
    temp = ac.imread("./tempr.jpg")
    bak = ac.imread("./target.jpg")
    pos = ac.find_template(bak, temp)
    try:
        distance = pos["rectangle"][0][0]
        return distance
    except:
        raise Temp_not_found_Error


if __name__ == "__main__":
    global info
    info = load_json()
    main()
