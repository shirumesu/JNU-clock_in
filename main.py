import os
import sys
import time
import smtplib
import requests
from loguru import logger

from src.mail import Mail
from src.config import Config
from src.driver import Chrome
from selenium.webdriver import ActionChains

EDIT = "2022-04-13"

if "--help" in sys.argv or "-h" in sys.argv:
    print(
        f"暨南大学自动打卡程序 启动参数一栏\n"
        f"--help / -h       查看启动参数的帮助\n"
        f"--no-update       启动,但不会自动更新\n"
        f"--reset           重置所有配置, 包括邮件设定、账号密码、当前所在地等\n"
        f"--reset-living    保留邮件设定、账号密码设定、重置当前所在地设定\n"
        f"示例: python ./main.py --no-update --reset\n"
        f"启动程序 但是不自动更新，并且重置所有设定"
    )
    sys.exit(0)


def check_update():
    logger.info("正在尝试自动检查更新……\n因为直连github 速度可能不理想 甚至无法连接 取消自动检查请使用启动参数`--no-update`")
    js = requests.get("https://api.github.com/repos/LYshiying/JNU-clock_in").json()
    if EDIT not in js["updated_at"]:
        logger.info("检测到程序有新版本！请在根目录使用`git pull`更新！")
        logger.info(f"本地当前版本: {EDIT}, github库中版本: {js['updated_at'][:10]}")
        logger.info("项目地址: https://github.com/LYshiying/JNU-clock_in")
        sys.exit(0)


if __name__ == "__main__":

    if "--no-update" not in sys.argv:
        check_update()

    os.makedirs("./images", exist_ok=True)

    if "--reset" in sys.argv:
        logger.info("检测到启动参数 '--reset', 将无视配置文件重新询问各类配置！")
        cfg = Config(reset=True)
    elif "--reset-living" in sys.argv:
        logger.info("检测到启动参数 '--reset-living', 将无视配置文件重新询问当前所在地！")
        cfg = Config(reset_living=True)
    else:
        cfg = Config()

    if cfg.send_mail:
        mail = Mail(cfg.sender, cfg.pw, cfg.receiv)
    else:
        mail = None

    # 创建webdriver
    chrome = Chrome(config=cfg)
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
        msg = "打卡失败!原因可能为:\n1. 您已完成今天的健康状态申报!\n2. 距离您上一次健康申报间隔还不足6小时\n请稍后再试"
        mail.send_email("【暨南大学打卡程序推送】", msg)
        logger.info("程序即将退出!")
        time.sleep(1)
        sys.exit(0)

    # 输入温度、当前所在地等信息提交
    try:
        suc, t1, t2, t3, lv = chrome.input_data()
        if suc:
            logger.info("提交成功!")
            msg = (
                "今日打卡成功!\n"
                "打卡信息:\n"
                f"早检温度: {t1[0]}, 日期: {'今日' if t1[1] else '昨日'}\n"
                f"午检温度: {t2[0]}, 日期: {'今日' if t2[1] else '昨日'}\n"
                f"晚检温度: {t3[0]}, 日期: {'今日' if t3[1] else '昨日'}\n"
                f"当前所在地址: {lv[0]} - {lv[1]} - {lv[2]}\n"
                f"当前所在地详细地址: {lv[3]}\n"
                f"近14天其他驻留城市: {lv[4]}"
            )
    except Exception as e:
        e = repr(e)
        logger.warning(
            f"无法填写数据(报错: {e}), 请手动打开网页查看是否学校又加了新玩意: https://stuhealth.jnu.edu.cn/#/login"
        )
        msg = f"今日打卡失败！！\n报错信息为: {e}"
    finally:
        try:
            if mail:
                mail.send_email("【暨南大学打卡程序推送】", msg)
        except smtplib.SMTPException as e:
            logger.warning("无法推送邮件, 请检查配置是否有误\n错误信息: {e}")

        logger.info("程序将于三秒后退出!")
        time.sleep(3)
        chrome.close_driver()
