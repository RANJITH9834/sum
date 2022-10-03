from re import M, sub
import sys
import requests
import json
import glob
import base64
import os
from datetime import datetime, timedelta
import logging
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
from configparser import ConfigParser
import pytz
import json
from decryptPWD import get_password
from alert import send_alert_email


def checkKey(dict, key):
    """It will check the given key exists in the response dictionary and return True or False"""
    if key in dict.keys():
        # print(dict[key])
        return True
    else:
        return False


def get_access_token(config_dic, app_id, client_secret, directory_id, user_name, password, logger, logHandler):
    """It will create a access token to access the mail apis"""
    app_id = app_id  # Application Id - on the azure app overview page
    client_secret = client_secret
    directory_id = directory_id
    token_url = "https://login.microsoftonline.com/" + directory_id + "/oauth2/token"
    token_data = {
        "grant_type": "password",
        "client_id": app_id,
        "client_secret": client_secret,
        "resource": "https://graph.microsoft.com",
        "scope": "https://graph.microsoft.com",
        "username": user_name,
        "password": password,
    }
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    logger.info(token_url)
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_dict = json.loads(token_response.text)
    error_exists = checkKey(token_response_dict, "error")
    if error_exists == True:
        password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                logHandler=logHandler)
        send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger, password=password,
                         message="Unable to get acces token",
                         mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                         mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                         email_body_html_file_path=config_dic.get('job1-configuration', 'failed_email_body_path'),
                         logHandler=logHandler)
        logger.critical("Unable to get access token")
        logger.critical(str(token_response_dict))
        logger.removeHandler(logHandler)
        raise Exception("Error in getting in access token")
    else:
        token = token_response_dict.get("access_token")
        refresh_token = token_response_dict.get("refresh_token")
        if token == None:
            logger.critical("Unable to get access token")
            logger.critical(str(token_response_dict))
            password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                    encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                    logHandler=logHandler)
            send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                             password=password, message="Unable to get acces token",
                             mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                             mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                             email_body_html_file_path=config_dic.get('job1-configuration', 'failed_email_body_path'),
                             logHandler=logHandler)
            logger.removeHandler(logHandler)
            raise Exception("Error in getting in access token")
        elif refresh_token == None:
            logger.critical("Unable to get refresh token")
            logger.critical(str(token_response_dict))
            password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                    encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                    logHandler=logHandler)
            send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                             password=password, message="Unable to get acces token",
                             mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                             mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                             email_body_html_file_path=config_dic.get('job1-configuration', 'failed_email_body_path'),
                             logHandler=logHandler)
            logger.removeHandler(logHandler)
            raise Exception("Error in getting in refresh token")
        else:
            # logger.info("getting access token completed")
            # logger.info("getting refresh token completed")
            return [token, refresh_token]


def message_ids(config_dic, token, mailFolder, app_id, client_secret, directory_id, user_name, password, logger,
                logHandler):
    """It will return the message ids which contains which satisifies the filter condition"""
    messages_ids_list = []
    mails_per_each_run = config_dic.get('dirobot-configuration', 'mails_per_each_run')
    messages_url = "https://graph.microsoft.com/v1.0/me/mailFolders('{folder}')/messages?$filter=((hasAttachments eq true))&$select=from,subject,id,hasAttachments&top={mails_per_each_run}".format(
        folder=mailFolder, mails_per_each_run=mails_per_each_run)
    # print(messages_url)
    logger.info(messages_url)
    while True:
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
        try:
            user_response_data = requests.get(messages_url, headers=headers)
        except Exception as msg:
            logger.error("Unable to get message details")
            logger.exception(msg)
            logger.removeHandler(logHandler)
            raise Exception(msg)
        user_response_dict = json.loads(user_response_data.text)
        error_exists = checkKey(user_response_dict, "error")
        # print(error_exists)
        if error_exists == True:
            if user_response_dict.get('error').get("message") == "Access token has expired or is not yet valid.":
                logger.warning("Access token expired retrying to get acces token")
                token_results = get_access_token(app_id=app_id, client_secret=client_secret, directory_id=directory_id,
                                                 user_name=user_name, password=password, logHandler=logHandler)
                token = token_results[0]
                logger.info("Access token generation completed ")
            else:
                logger.error("unable to get the messages")
                logger.exception(str(user_response_dict))
                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                        encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                        logHandler=logHandler)
                send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                 password=password, message="unable to get messages",
                                 mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                          'failed_email_body_path'),
                                 logHandler=logHandler)
                logger.removeHandler(logHandler)
                raise Exception(str(user_response_dict))
        else:
            if user_response_dict.get('value', None) == None:
                logger.error("unable to get the messages from response")
                logger.exception(str(user_response_dict))
                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                        encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                        logHandler=logHandler)
                send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                 password=password, message="unable to get messages",
                                 mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                          'failed_email_body_path'),
                                 logHandler=logHandler)
                logger.removeHandler(logHandler)
                raise Exception(str(user_response_dict))
            else:
                if len(list(user_response_dict.get('value'))) > 0:
                    for x in user_response_dict.get('value'):
                        logger.error("current processing email object " + str(x))
                        message_dict = {}
                        try:
                            message_id = x['id']
                        except Exception as msg:
                            logger.error("unable to get the message ids for the email object " + str(x))
                            logger.exception(str(user_response_dict))
                            password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'),
                                                    logger=logger,
                                                    encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                                    logHandler=logHandler)
                            send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                             password=password, message="unable to get message ids",
                                             mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(
                                                 ","),
                                             mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                             email_body_html_file_path=config_dic.get('job1-configuration',
                                                                                      'failed_email_body_path'),
                                             logHandler=logHandler)
                            logger.removeHandler(logHandler)
                            raise Exception("unable to get the message ids")
                        try:
                            message_subject = x.get('subject')
                        except Exception as msg:
                            logger.error("unable to get the subject for the email object " + str(x))
                            logger.exception(msg)
                            password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'),
                                                    logger=logger,
                                                    encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                                    logHandler=logHandler)
                            send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                             password=password, message="unable to get subject from the messages",
                                             mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(
                                                 ","),
                                             mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                             email_body_html_file_path=config_dic.get('job1-configuration',
                                                                                      'failed_email_body_path'),
                                             logHandler=logHandler)
                            logger.removeHandler(logHandler)
                            raise Exception("unable to get the subject from emails")
                        try:
                            message_address = x.get('from').get('emailAddress').get('address')
                        except Exception as msg:
                            logger.error("unable to get the email Address for the email object " + str(x))
                            logger.exception(msg)
                            password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'),
                                                    logger=logger,
                                                    encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                                    logHandler=logHandler)
                            send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                             password=password, message="unable to get subject from the messages",
                                             mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(
                                                 ","),
                                             mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                             email_body_html_file_path=config_dic.get('job1-configuration',
                                                                                      'failed_email_body_path'),
                                             logHandler=logHandler)
                            logger.removeHandler(logHandler)
                            raise Exception("unable to get the subject from emails")
                        message_dict[message_id] = [message_subject, message_address]
                        messages_ids_list.append(message_dict)
                        # print(x['subject'])
                    if "@odata.nextLink" in user_response_dict.keys():
                        messages_url = user_response_data['@odata.nextLink']
                    else:
                        logger.info("Got emails")
                        break
                else:
                    # print("no emails")
                    logger.info("no mails")
                    break
    return messages_ids_list, token


def get_attachments(config_dic, token, message_id, FileDirectory, specific_folder, app_id, client_secret, directory_id,
                    user_name, password, logger, logHandler, partnerName, filename=None, errorMessage=""):
    """This function will download the attachemnts for the given message id"""
    specific_full_path = os.path.join(FileDirectory, specific_folder)
    temp_full_path = os.path.join(FileDirectory, "temp")

    if not os.path.isdir(temp_full_path):
        os.makedirs(temp_full_path)
    if len(os.listdir(temp_full_path)) > 0:
        for f in os.listdir(temp_full_path):
            os.remove(os.path.join(temp_full_path, f))
    isdir = os.path.isdir(specific_full_path)
    if not isdir:
        os.makedirs(specific_full_path)
    if len(os.listdir(specific_full_path)) > 0:
        for f in os.listdir(specific_full_path):
            os.remove(os.path.join(specific_full_path, f))
    while True:
        Attachments_url = "https://graph.microsoft.com/v1.0/me/mailFolders('Inbox')/messages/" + message_id + "/attachments"
        logger.info(Attachments_url)
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
        try:
            user_attachment_data = json.loads(requests.get(Attachments_url, headers=headers).text)
        except Exception as msg:
            logger.error("unable to download email attachments")
            logger.exception(msg)
            logger.removeHandler(logHandler)
            raise Exception("unable to download email attachments")
        # print(user_attachment_data)
        error_exists = checkKey(user_attachment_data, "error")
        # print(error_exists)
        if error_exists == True:
            if user_attachment_data.get('error').get("message") == "Access token has expired or is not yet valid.":
                logger.warning("Access token expired retrying to get acces token")
                token_results = get_access_token(app_id=app_id, client_secret=client_secret, directory_id=directory_id,
                                                 user_name=user_name, password=password, logHandler=logHandler)
                token = token_results[0]
                logger.removeHandler(logHandler)
                # logger.info("Access token generation completed ")
            else:
                logger.error("unable to get the attachments")
                logger.exception(str(user_attachment_data))
                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                        encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                        logHandler=logHandler)
                send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                 password=password, message="unable to get attachments from the email",
                                 mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                          'failed_email_body_path'),
                                 logHandler=logHandler)
                logger.removeHandler(logHandler)
                raise Exception(str(user_attachment_data))
        else:
            if user_attachment_data.get('value', None) == None:
                logger.error("unable to get the attachments from response ")
                logger.exception(str(user_attachment_data))
                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                        encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                        logHandler=logHandler)
                send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                 password=password, message="unable to get attachments from the email",
                                 mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                          'failed_email_body_path'),
                                 logHandler=logHandler)
                logger.removeHandler(logHandler)
                raise Exception(str(user_attachment_data))
            elif user_attachment_data.get('value')[0].get('contentType', None) == None:
                logger.error("unable to get the attachments from response")
                logger.exception(str(user_attachment_data))
                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                        encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                        logHandler=logHandler)
                send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                 password=password, message="unable to get type of attachments",
                                 mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                          'failed_email_body_path'),
                                 logHandler=logHandler)
                logger.removeHandler(logHandler)
                raise Exception(str(user_attachment_data))
            elif user_attachment_data.get('value')[0].get('name', None) == None:
                logger.error(
                    "unable to get the attachments from response " + user_attachment_data.get('value')[0].get('name',
                                                                                                              None))
                logger.exception(str(user_attachment_data))
                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                        encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                        logHandler=logHandler)
                send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                 password=password, message="unable to get name of the attachments",
                                 mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                          'failed_email_body_path'),
                                 logHandler=logHandler)
                logger.removeHandler(logHandler)
                raise Exception(str(user_attachment_data))
            else:
                counter = 0
                for y in user_attachment_data['value']:
                    if y['contentType'] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or y[
                        'contentType'] == "application/vnd.ms-excel" or y[
                        'contentType'] == "application/octet-stream" or y['contentType'] == "text/csv":
                        counter = counter + 1
                current_iteration = 1
                for y in user_attachment_data['value']:
                    if counter == 1:
                        logger.info("Email has one excel file as attachment")
                        if y['contentType'] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or y[
                            'contentType'] == "application/vnd.ms-excel" or y[
                            'contentType'] == "application/octet-stream" or y['contentType'] == "text/csv":
                            try:
                                actual_filename = str(y['name']).split(".")
                                UTC = pytz.utc
                                now = datetime.now(UTC)
                                dt_string = now.strftime("-%b-%d-%Y-%H-%M-%S.")
                                modified_filename = filename + dt_string + actual_filename[-1]
                                # print(modified_filename)
                                fname = os.path.join(specific_full_path, modified_filename)
                                f = open(fname, "w+b")
                                f.write(base64.b64decode(y['contentBytes']))
                                logger.info("file downloaded to " + os.path.join(specific_full_path, modified_filename))
                            except Exception as msg:
                                logger.error("unable to download the attachments from response " + str(y['name']))
                                logger.exception(str(msg))
                                password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'),
                                                        logger=logger,
                                                        encryptionPwd=config_dic.get('job1-configuration',
                                                                                     'encryptedpwd'),
                                                        logHandler=logHandler)
                                send_alert_email(username=config_dic.get('job1-configuration', 'username'),
                                                 logger=logger, password=password,
                                                 message="unable to download the attachment",
                                                 mail_to_list=config_dic.get('job1-configuration',
                                                                             'notify_mails').split(","),
                                                 mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                                 email_body_html_file_path=config_dic.get('job1-configuration',
                                                                                          'failed_email_body_path'),
                                                 logHandler=logHandler)
                                logger.removeHandler(logHandler)
                                raise Exception("unable to download the attachments from response")
                            finally:
                                f.close()

                    else:
                        logger.info("email has multiple attachments but mgu is not configured ")
                        break

        break


def move_message(config_dic, token, message_id, subject, move_folder, app_id, client_secret, directory_id, user_name,
                 password, logger, logHandler):
    counter = 0
    while True:
        move_url = "https://graph.microsoft.com/v1.0/me/messages/{messageId}/move".format(messageId=message_id)
        logger.info(move_url)
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
        move_data = {"destinationId": "{move_folder}".format(move_folder=move_folder)}
        move_data = json.dumps(move_data)
        try:
            response = requests.post(move_url, data=move_data, headers=headers)
        except Exception as msg:
            logger.error("unable to move the emails " + message_id)
            logger.exception(msg)
            password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                    encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                    logHandler=logHandler)
            send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                             password=password,
                             message="unable to move the message to deleted folder with subject " + subject,
                             mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                             mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                             email_body_html_file_path=config_dic.get('job1-configuration', 'failed_email_body_path'),
                             logHandler=logHandler)
            logger.removeHandler(logHandler)
            raise Exception("unable to move the email")
        if response.status_code >= 200 and response.status_code < 300:
            logger.info("Message moved successfully " + message_id)
            break
        else:
            moved_response = json.loads(response.text)
            logger.error("Unable to move the mail")
            error_exists = checkKey(moved_response, "error")
            if error_exists == True:
                if moved_response.get('error').get("message") == "Access token has expired or is not yet valid.":
                    logger.warning("Access token expired retrying to get acces token")
                    token_results = get_access_token(app_id=app_id, client_secret=client_secret,
                                                     directory_id=directory_id, user_name=user_name, password=password,
                                                     logHandler=logHandler)
                    token = token_results[0]
                    logger.info("Access token generation completed ")
                else:
                    logger.error("unable to move the attachment")
                    logger.exception(str(moved_response))
                    if counter == 2:
                        password = get_password(refKey=config_dic.get('job1-configuration', 'refkey'), logger=logger,
                                                encryptionPwd=config_dic.get('job1-configuration', 'encryptedpwd'),
                                                logHandler=logHandler)
                        send_alert_email(username=config_dic.get('job1-configuration', 'username'), logger=logger,
                                         password=password,
                                         message="unable to move the message to deleted folder with subject " + subject,
                                         mail_to_list=config_dic.get('job1-configuration', 'notify_mails').split(","),
                                         mail_subject=config_dic.get('job1-configuration', 'failed_suject'),
                                         email_body_html_file_path=config_dic.get('job1-configuration',
                                                                                  'failed_email_body_path'),
                                         logHandler=logHandler)
                        logger.removeHandler(logHandler)
                        raise Exception(moved_response)
                    counter = counter + 1


def main(config_dic, dbconfig_dict, postgreSQL_pool, kafka_producer):
    """This is the main which is scheduled for every run"""
    try:
        mailFolder = config_dic.get('dirobot-configuration', 'mailfolder')
        FileDirectory = config_dic.get('dirobot-configuration', 'attachmentsDirectory')
        app_id = config_dic.get('dirobot-configuration', 'app_id')
        client_secret = config_dic.get('dirobot-configuration', 'client_secret')
        directory_id = config_dic.get('dirobot-configuration', 'directory_id')
        username = config_dic.get('job1-configuration', 'username')
        ref_key = config_dic.get('job1-configuration', 'refkey')
        encrypted_pwd = config_dic.get('job1-configuration', 'encryptedpwd')
        logs_path = config_dic.get('job1-configuration', 'logspath')
        move_folder = config_dic.get('dirobot-configuration', 'movefolder')
        DefaultSenders = config_dic.get('dirobot-configuration', 'default_senders')
        email_domains = config_dic.get('dirobot-configuration', 'email_domains')
    except Exception as msg:
        print(msg)
        raise Exception(str(msg))
    # getting date and time for log file creation
    now = datetime.now()
    log_file_name = "Log-" + now.strftime("%m-%d-%Y-%H-%M")
    logs_full_path = Path(logs_path, log_file_name + '.log')
    # print(logs_full_path)
    try:
        now = datetime.now()
        log_file_name = "Log-" + now.strftime("%m-%d-%Y") + ".log"
        logs_full_path = os.path.join(logs_path, log_file_name)
        formatter = logging.Formatter(
            '[%(asctime)s | %(levelname)s] ["job3"] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s')
        file_handler = logging.FileHandler(logs_full_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger = logging.getLogger('apscheduler.executors.default')
        logger.propagate = False
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.info("Job3 Execution started")
    except FileNotFoundError as msg:
        if not os.path.isdir(logs_path):
            os.makedirs(logs_path, exist_ok=True)
            now = datetime.now()
            log_file_name = "Log-" + now.strftime("%m-%d-%Y") + ".log"
            logs_full_path = os.path.join(logs_path, log_file_name)
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(asctime)s | %(levelname)s] ["job3"] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s')
            file_handler = logging.FileHandler(logs_full_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    except Exception as msg:
        print(msg)
        raise Exception(msg)
        # logger.info("Execution stopped")
    try:
        password = get_password(encryptionPwd=encrypted_pwd, refKey=ref_key, logger=logger, logHandler=file_handler)
    except Exception as msg:
        # print("unable to decrypt the password")
        logger.error("unable to decrypt the password")
        raise Exception(msg)

    token_results = get_access_token(config_dic=config_dic, app_id=app_id, client_secret=client_secret,
                                     directory_id=directory_id, user_name=username, password=password, logger=logger,
                                     logHandler=file_handler)
    # print(token_results[0])
    token = token_results[0]
    # print(token)
    messages_ids_list_and_token = message_ids(config_dic=config_dic, token=token, mailFolder=mailFolder, app_id=app_id,
                                              client_secret=client_secret, directory_id=directory_id,
                                              user_name=username, password=password, logger=logger,
                                              logHandler=file_handler)
    messages_ids_list = messages_ids_list_and_token[0]
    token = messages_ids_list_and_token[1]
    # print(messages_ids_list)
    if len(messages_ids_list) != 0:
        DefaultSender = DefaultSenders.split(',')
        DefaultSenders = [x.strip().lower() for x in DefaultSender]
        email_domains = email_domains.split(",")
        for message_id_dict in messages_ids_list:

            for message_id, subject_and_fromAddress_list in message_id_dict.items():
                # print(message_id)
                # print(subject_and_fromAddress_list)
                subject = subject_and_fromAddress_list[0]
                fromAddress = subject_and_fromAddress_list[1].lower()
                subject_list = [s.strip() for s in subject.lower().split("-")]
                fromAddress_domain = fromAddress.split("@")[1]
                # print(fromAddress_domain)
                domain_filter = ""
                if fromAddress in DefaultSenders:
                    domain_filter = ""
                    logger.info("Mail was received from default sender")
                elif fromAddress_domain in email_domains:
                    domain_filter = fromAddress
                    logger.info("The mail domain is not official domain " + fromAddress_domain)
                else:
                    domain_filter = fromAddress_domain
                    logger.info("The mail domain is official email domain " + fromAddress_domain)
                logger.info(subject_list)
    logger.info("job3 Execution completed")
    logger.removeHandler(file_handler)



