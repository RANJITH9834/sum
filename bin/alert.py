import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from outlook import outlook_graph_apis


def send_alert_email(username, password, message, mail_to_list, mail_subject, email_body_html_file_path, logger,
                     log_handler, other_details=None):
    """This function reads the html file and add it to the body and sent the email from specified 
        to the mentioned list of email address"""
    if other_details:
        outlook_graph_apis.move_message(other_details['access_token'], other_details['message_id'],
                                        other_details['move_folder'])
    logger.info("sending failure email")
    try:
        with open(email_body_html_file_path, "r", encoding='utf-8') as f:
            mail_body = f.read()
    except FileNotFoundError as msg:
        # print(email_body_html_file_path+" file not found")
        logger.error("unable to find the " + email_body_html_file_path + " file")
        logger.removeHandler(log_handler)
        raise FileNotFoundError(msg)
    except Exception as msg:
        # print(msg)
        logger.error("unable to find the " + email_body_html_file_path + " file")
        logger.removeHandler(log_handler)
        raise Exception(msg)
    mail_body = mail_body.replace("[x]", message)
    new_mails = ''
    Counter = 0
    for x in mail_to_list:
        if Counter == 0:
            new_mails = new_mails + "<" + x.strip() + ">"
        else:
            new_mails = new_mails + ",<" + x.strip() + ">"
        Counter = Counter + 1
    mimemsg = MIMEMultipart()
    mimemsg['From'] = username
    mimemsg['To'] = new_mails
    # print(new_mails)
    mimemsg['Subject'] = mail_subject
    mimemsg.attach(MIMEText(mail_body, 'html'))
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(username, password)
            server.sendmail(username, mail_to_list, mimemsg.as_string())
    except Exception as msg:
        # print("unable to send the alert mail")
        logger.error("unable to send the alert mail")
        logger.removeHandler(log_handler)
        raise Exception(msg)

# send_alert_email(username="di-robot@fortegra.onmicrosoft.com",password="#Fort@22.k",email_body_html_file_path="C:\\Users\\Venkat\\Desktop\\fortegra-project\\di-robot\\di-robot\\conf\\email.html",mail_subject="testtttting the mail",mail_to_list=['venkat.sai.thota@outlook.com','venkat.sai@kanerika.com'])
