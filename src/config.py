import json
import random
from typing import *
from loguru import logger


class Config:
    def __init__(self, reset: bool = False, reset_living: bool = False) -> None:
        self.load_config(reset, reset_living)

        if self.send_mail is None:
            ans = input("请问是否需要邮件推送?\n1.需要\n2.不需要\n请回复数字:")
            self.send_mail = not (int(ans) - 1)
            self.dump()
        if self.send_mail and not (self.sender and self.pw and self.receiv):
            suc = False
            while not suc:
                self.sender = input("请输入发件人邮箱(可以自己发送给自己): ")
                self.pw = input(
                    "请输入发件人密码(qq,163为授权码, 获取方式请见 https://service.mail.qq.com/cgi-bin/help?subtype=1&id=28&no=1001256 请开启 POP3/SMTP or IMAP/SMTP): "
                )
                self.receiv = input("请输入收件人邮箱, 需要群发请用空格隔开多个邮箱: ").split(" ")
                s = input(
                    "邮件推送配置成功!\n"
                    f"发件人: {self.sender}\n"
                    f"发件人密码: {self.pw}\n"
                    f"收件人: {self.receiv}\n"
                    f"如果有错误请输入 -1 否则请按enter"
                )
                if s and int(s) == -1:
                    continue
                else:
                    self.dump()
                    break

    def load_config(self, reset: bool, reset_living: bool) -> None:
        try:
            if reset:
                raise RuntimeError
            with open("./source/config.json", "r", encoding="utf-8") as f:
                dt = json.load(f)
            self.send_mail = dt["send_mail"]
            self.sender = dt["sender"]
            self.pw = dt["mail_pw"]
            self.receiv = dt["receiv"]
            self.UserName = dt["UserName"]
            self.Passwd = dt["Passwd"]
            if reset_living:
                self.Province = None
                self.City = None
                self.District = None
                self.Living = None
                self.other_city = None
            else:
                self.Province = dt["Province"]
                self.City = dt["City"]
                self.District = dt["District"]
                self.Living = dt["Living"]
                self.other_city = dt["other_city"]

        except Exception as e:
            logger.info("检测到首次运行此程序, 在稍后会要求输入信息……")
            self.UserName = None
            self.Passwd = None
            self.Province = None
            self.City = None
            self.District = None
            self.Living = None
            self.other_city = None

            self.send_mail = None
            self.sender = None
            self.pw = None
            self.receiv = None

    def get_user(self, Re: bool = False) -> list[str]:
        if Re or not (self.UserName and self.Passwd):
            self.UserName = input("请输入你的学号用作登录(仅需首次运行输入一次)")
            self.Passwd = input("请输入你的密码用作登录(仅需首次运行输入一次)")
            c = input("如果有错误输入请输入任意字符 否则请按Enter")
            if c:
                return self.get_user(Re=True)
            self.dump()
        return [self.UserName, self.Passwd]

    def random_temp(self) -> int:
        t = round(random.uniform(36.1, 36.9), 1)
        logger.debug(f"生成温度为: {t}")
        return str(t)

    def get_living(self) -> Union[List[str], None]:
        return (
            [self.Province, self.City, self.District, self.Living, self.other_city]
            if (
                self.Province
                and self.City
                and self.District
                and self.Living
                and self.other_city
            )
            else None * 5
        )

    def set_living(self, P, C, D, L, O) -> None:
        self.Province = P
        self.City = C
        self.District = D
        self.Living = L
        self.other_city = O
        self.dump()

    def dump(self) -> None:
        with open("./source/config.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "UserName": self.UserName,
                    "Passwd": self.Passwd,
                    "Province": self.Province,
                    "City": self.City,
                    "District": self.District,
                    "Living": self.Living,
                    "other_city": self.other_city,
                    "send_mail": self.send_mail,
                    "sender": self.sender,
                    "mail_pw": self.pw,
                    "receiv": self.receiv,
                },
                f,
                ensure_ascii=False,
                indent=4,
            )
            logger.info("成功保存配置, 下次启动时将不再需要输入数据")
