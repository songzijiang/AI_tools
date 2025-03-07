import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
from tools.general import get_config


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


class Mail:
    def description(self):
        return {'param数量': 3, '描述': '给指定邮箱发送邮件,param1为目标邮箱地址,param2为邮件主题,param3为邮件内容'}

    def get_parameters(self):
        return 'query'

    def __init__(self, config, default_config):
        self.smtp_server = get_config(config, default_config, ('mail', 'host'))
        self.smtp_port = get_config(config, default_config, ('mail', 'port'))
        self.user = get_config(config, default_config, ('mail', 'user'))
        self.password = get_config(config, default_config, ('mail', 'password'))

    def send_mail(self, to_addr, subject, content):
        print('开始发送邮件...')
        try:
            # return '邮件发送成功'
            print(to_addr, subject, content)
            smtpObj = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(self.user, self.password)
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = _format_addr('AI小助手 <%s>' % self.user)
            message['To'] = _format_addr('目标用户 <%s>' % to_addr)
            message['Subject'] = Header(subject, 'utf-8')
            smtpObj.sendmail(self.user, [to_addr], message.as_string())
            smtpObj.quit()
            print('邮件发送成功,目标邮箱:', to_addr, '邮件主题:', subject)
            return '邮件发送成功'
        except Exception as e:
            print('邮件发送失败:', e)
            return '邮件发送失败'
