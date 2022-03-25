import json
import random
from typing import *
from loguru import logger


class Config:
    def __init__(self) -> None:
        self.UserName = None
        self.Passwd = None
        self.Province = None
        self.City = None
        self.District = None
        try:
            self.load_config()
        except Exception as e:
            logger.info("检测到首次运行此程序, 在稍后会要求输入信息")

    def load_config(self) -> None:
        with open("./source/config.json", "r", encoding="utf-8") as f:
            dt = json.load(f)
        self.UserName = dt["UserName"]
        self.Passwd = dt["Passwd"]
        self.Province = dt["Province"]
        self.City = dt["City"]
        self.District = dt["District"]

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
            [self.Province, self.City, self.District]
            if (self.Province and self.City and self.District)
            else None
        )

    def set_living(self, P, C, D) -> None:
        self.Province = P
        self.City = C
        self.District = D
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
                },
                f,
                ensure_ascii=False,
                indent=4,
            )
            logger.info("成功保存配置, 下次启动时将不再需要输入数据")
