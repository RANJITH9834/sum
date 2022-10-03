import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import logging


def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield os.path.join(os.path.join(path, file))


def send_email(username, password, to_recipients, email_subject, email_body, attachment_files_path, cc_mails=None):
    try:
        print("email sending started")
        new_mails = ""
        Counter = 0
        for x in to_recipients:
            if Counter == 0:
                new_mails = new_mails + "<" + x.strip() + ">"
            else:
                new_mails = new_mails + ",<" + x.strip() + ">"
            Counter = Counter + 1

        send_from = username
        # extension = attachment_file_path.rsplit(".",1)[0]

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = new_mails
        if cc_mails:
            msg['CC'] = ','.join([f'<{mail.strip()}>' for mail in cc_mails])
        msg['Subject'] = email_subject
        msg.attach(MIMEText(email_body, 'html'))
        # Add Attachment
        if os.path.isdir(attachment_files_path):
            files_list = get_files(attachment_files_path)
            for each_file in files_list:
                if each_file.lower().endswith(".htm") or each_file.lower().endswith('.html'):
                    continue
                filename = os.path.basename(each_file)
                # file_full_path = os.path.join(os.path.dirname(each_file), filename)
                # print(file_full_path)
                print('line-1 - ', each_file)
                with open(each_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                # Set mail headers
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(send_from, password)
            server.sendmail(send_from, to_recipients + cc_mails if cc_mails else to_recipients, msg.as_string())
    except Exception as msg:
        print(msg)
        raise Exception("unable to send email")


# logs_path = "C:\\Users\\Venkat\\Desktop"
# now = datetime.datetime.now()
# log_file_name = "Log-" + now.strftime("%m-%d-%Y") + ".log"
# logs_full_path = os.path.join(logs_path, log_file_name)
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# formatter = logging.Formatter(
#     '[%(asctime)s | %(levelname)s] ["job3"] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s')
# file_handler = logging.FileHandler(logs_full_path)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
# send_email(username="di-robot@fortegra.onmicrosoft.com", password="#Fort@22.k", to_recipients=(
#     'venkat.sai@kanerika.com','training@kanerika.com'), email_subject="test", email_body="PFA attached file",
#            attachment_files_path="C:\\Users\\Venkat\\Desktop\\decryptedEmailAttachments", logger=logger)
# logger.removeHandler(file_handler)
