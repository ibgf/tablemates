import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465  # SSL 端口
SMTP_USERNAME = "kmcqdfp@163.com"
SMTP_PASSWORD = "SRtxXzmH8fjy2U2k"  # 163 邮箱授权码（不是邮箱密码）

def generate_verification_code(length=6):
    """
    生成一个 4-6 位随机验证码
    """
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def send_verification_email(email: str, code: str):
    subject = "TableMates 账户激活验证码"
    body = f"您的验证码是：{code}\n请在 10 分钟内完成激活。"

    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # 使用 SMTP_SSL 连接 163 邮箱
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, email, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
        return True
    except Exception as e:
        print("❌ 邮件发送失败:", e)
        return False

