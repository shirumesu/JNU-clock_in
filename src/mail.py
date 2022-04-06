import smtplib
from email.mime.text import MIMEText

from loguru import logger
from typing import List, Union


class Mail:
    def __init__(self, sender: str, pw: str, receiv: Union[str, List[str]]) -> None:
        """初始化邮件信息, 默认使用 SMTP 服务

        Args:
            sender (str): 发送者邮箱
            pw (str): 发送者密码(163 qq为授权码)
            receiv (List[str]): 收件人邮箱
        """
        try:
            self.host = "smtp." + sender.split("@")[1]
            self.user = sender.split("@")[0]
        except IndexError as e:
            logger.debug(f"host user加载错误, sender项: {sender}, 错误: {e}")
            logger.warning("请确保sender一项为: xxxxxx@yy.zzz")
        self.passwd = pw
        self.sender = sender
        self.receivers = receiv if isinstance(receiv, list) else [receiv]

    def send_email(self, title: str, content: str) -> None:
        """发送邮件

        Args:
            title (str): 标题
            content (str): 内容
        """
        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = title
        msg["From"] = self.sender
        msg["To"] = self.receivers[0]

        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.host, 25)
            smtp.login(self.user, self.passwd)
            smtp.sendmail(self.sender, self.receivers, msg.as_string())
            logger.info("邮件发送成功!")
        except smtplib.SMTPException as e:
            logger.warning(f"邮件发送失败: {e}")
            raise e
