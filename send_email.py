import schedule
import time
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import socket
import logging


def message(subject="Python Notification",
            text="", img=None, attachment=None):

    msg = MIMEMultipart()

    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    if img is not None:
        if type(img) is not list:
            img = [img]

        for one_img in img:
            img_data = open(one_img, 'rb').read()
            msg.attach(MIMEImage(img_data,
                                 name=os.path.basename(one_img)))

    if attachment is not None:
        if type(attachment) is not list:
            attachment = [attachment]

        for one_attachment in attachment:
            with open(one_attachment, 'rb') as f:
                file = MIMEApplication(
                    f.read(),
                    name=os.path.basename(one_attachment)
                )
            file['Content-Disposition'] = f'attachment;\
            filename="{os.path.basename(one_attachment)}"'
            msg.attach(file)
    return msg


def mail():
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()

    from_addr = os.getenv('email_address')

    smtp.login(from_addr, os.getenv('email_passwd'))

    msg = message("IP Address", socket.gethostbyname(socket.gethostname()))

    to_addrs = [os.getenv('send_to_email_address')]

    smtp.sendmail(from_addr=from_addr,
                  to_addrs=to_addrs, msg=msg.as_string())

    smtp.quit()


schedule.every().day.at("18:00").do(mail)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler = logging.FileHandler('send_email.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

while True:
    try:
        schedule.run_pending()
    except Exception as e:
        logger.error(e)
    time.sleep(1)
