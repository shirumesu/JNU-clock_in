import os
import sys
import time
from loguru import logger
from src.driver import Chrome
from selenium.webdriver import ActionChains

if __name__ == "__main__":

    os.makedirs("./images", exist_ok=True)

    # 创建webdriver
    chrome = Chrome()
    # 访问打卡网页
    chrome.get("https://stuhealth.jnu.edu.cn/#/login")

    # 输入账号密码
    chrome.input_passwd()
    # 滑条验证
    while not chrome.crack():
        s = chrome.crack()
        if s:
            break

    # 点击登录按钮后等待一秒加载
    ActionChains(chrome.driver).move_to_element(chrome.login_button).click(
        chrome.login_button
    ).perform()
    time.sleep(1)

    # 检查是否已经成功打卡 如果是 退出程序
    if chrome.is_clock_in():
        logger.info("程序即将退出!")
        time.sleep(1)
        sys.exit(0)

    # 输入温度、当前所在地等信息提交
    try:
        if chrome.input_data():
            logger.info("提交成功!,三秒后即将退出程序")
            time.sleep(3)
        else:
            raise RuntimeError
    except Exception as e:
        logger.warning(
            f"无法填写数据(报错: {e}), 请手动打开网页查看是否学校又加了新玩意: https://stuhealth.jnu.edu.cn/#/login"
        )
    finally:
        chrome.close_driver()
