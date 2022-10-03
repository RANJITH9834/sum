import os
import re
from datetime import datetime
import logging
from pathlib import Path
from decryptPWD import get_password
from outlook import outlook_graph_apis
from getEmails import get_all_email_address
from getPasswordFromExcel import get_excel_password
from web_automations import marinerfinance_automation
from send_email_with_attachment import send_email
from alert import send_alert_email


def delete_folder(folder):
    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        if os.path.isdir(full_path):
            delete_folder(full_path)
            os.rmdir(full_path)
        else:
            os.remove(full_path)


def main(config_dic):
    """This is the main which is scheduled for every run"""
    try:
        print("in main")
        mail_folder = config_dic.get('decrypt-configuration', 'mailfolder')
        file_directory = config_dic.get('decrypt-configuration', 'file_directory')
        download_directory = config_dic.get('decrypt-configuration', 'download_directory')
        app_id = config_dic.get('decrypt-configuration', 'app_id')
        client_secret = config_dic.get('decrypt-configuration', 'client_secret')
        directory_id = config_dic.get('decrypt-configuration', 'directory_id')
        user_name = config_dic.get('decrypt-configuration', 'username')
        ref_key = config_dic.get('decrypt-configuration', 'refkey')
        encrypted_pwd = config_dic.get('decrypt-configuration', 'encryptedpwd')
        logs_path = config_dic.get('decrypt-configuration', 'logspath')
        move_folder = config_dic.get('decrypt-configuration', 'movefolder')
        password_excel_file_path = config_dic.get('decrypt-configuration', 'password_excel_file_path')
        email_body = config_dic.get('decrypt-configuration', 'email_body')
        notify_mails = config_dic.get('decrypt-configuration','notify_mails').split(",")
        failed_suject = config_dic.get('decrypt-configuration','failed_suject')
        failed_email_body_path = config_dic.get('decrypt-configuration', 'failed_email_body_path')
        mails_per_each_run = config_dic.get('decrypt-configuration','mails_per_each_run')
        cc_mail_ids = [mail.strip() for mail in config_dic.get('decrypt-configuration', 'cc_mails').split(',')]
        try:
            print('removing all previous downloads')
            delete_folder(file_directory)
        except:
            pass

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

    try:
        list_of_access_and_refresh_token = outlook_graph_apis.get_access_token(app_id=app_id, client_secret=client_secret,
                                                                           directory_id=directory_id,
                                                                           user_name=user_name,
                                                                           password=password,logger=logger)
    except Exception as msg:
        send_alert_email(username=user_name,password=password,message="unable to get access token",mail_to_list=notify_mails,mail_subject=failed_suject,email_body_html_file_path=failed_email_body_path,logger=logger,log_handler=file_handler)
        logger.info("execution stopped")
        logger.removeHandler(file_handler)
        raise Exception("Unable to get access token")
    # print(list_of_access_and_refresh_token)
    access_token = list_of_access_and_refresh_token[0]
    try:
        message_id_list_json = outlook_graph_apis.message_ids(token=access_token, mail_folder=mail_folder,
                                                          mails_per_each_run = mails_per_each_run,logger=logger)
    except Exception as msg:
        message = str(msg)
        message, msg_id = message.split(':')
        send_alert_email(username=user_name,password=password,message=f"",
                         mail_to_list=notify_mails,mail_subject=failed_suject,
                         email_body_html_file_path=failed_email_body_path,
                         logger=logger,log_handler=file_handler, other_details={'access_token': access_token,
                                                                                'message_id': msg_id,
                                                                                'move_folder': move_folder})
        logger.info("execution stopped")
        logger.removeHandler(file_handler)
        raise Exception("Unable to get message id's")
    if len(message_id_list_json) == 0:
        import sys
        sys.exit(0)
    # print(message_id_list_json[0])
    # print(len(message_id_list_json))
    logger.info("message_id_list_json is : ")
    logger.info(message_id_list_json)
    for each_message_id in message_id_list_json:
        # print(each_message_id)
        for message_id, content_list in each_message_id.items():
            # message_id_without_sym = re.sub('[^a-zA-Z0-9]', '', message_id)
            # if message_id_without_sym in os.listdir(file_directory):
            #     continue
            # print(message_id)
            message_subject = content_list[0]
            message_address = content_list[1]
            message_body_html = content_list[2]
            message_sender_name = content_list[3]
            message_to_addresses = content_list[4]
            print(message_subject)
            #print(message_body_html)
            logger.info('current processing email is - '+message_subject)
            try:
                normal_files_exists = outlook_graph_apis.get_attachments(token=access_token, mail_folder=mail_folder,
                                                                 message_id=message_id,
                                                                 file_directory=file_directory,logger=logger)
            # print(attachment_path)
            except Exception as msg:
                send_alert_email(username=user_name, password=password, message=f"",
                                 mail_to_list=notify_mails, mail_subject=failed_suject,
                                 email_body_html_file_path=failed_email_body_path, logger=logger,
                                 log_handler=file_handler)
                logger.info("execution stopped")
                logger.removeHandler(file_handler)
                raise Exception("Unable to get attachment for the email - "+message_subject)
            logger.info("encrypted email downloading completed")
            logger.info("getting actual (from and to address) from the email html body ")
            try:
                from_and_to_mails_dict = get_all_email_address(contents=message_body_html)
            except Exception as msg:
                send_alert_email(username=user_name, password=password,
                                 message="Unable to get from and to addresses from the email body",
                                 mail_to_list=notify_mails, mail_subject=failed_suject,
                                 email_body_html_file_path=failed_email_body_path, logger=logger,
                                 log_handler=file_handler)
                logger.info("execution stopped")
                logger.removeHandler(file_handler)
                raise Exception("Unable to get from and to addresses from the email body")
            print(from_and_to_mails_dict)
            from_address_in_the_body = from_and_to_mails_dict['from_email_address']
            to_address_in_the_body = from_and_to_mails_dict['to_email_address']
            if from_address_in_the_body == '' or len(to_address_in_the_body) == 0:
                from_and_to_mails_dict = {**from_and_to_mails_dict, 'from_email_address': message_address,
                                          'to_email_address': message_to_addresses,
                                          'from_email_name': message_sender_name, 'subject': message_subject}
                from_address_in_the_body = from_and_to_mails_dict['from_email_address']
                to_address_in_the_body = from_and_to_mails_dict['to_email_address']
                # logger.error("Unable to get from and to addresses from the email body "+message_subject)
                # send_alert_email(username=user_name, password=password,
                #                  message="Unable to get from and to addresses from the email body "+message_subject,
                #                  mail_to_list=notify_mails, mail_subject=failed_suject,
                #                  email_body_html_file_path=failed_email_body_path, logger=logger,
                #                  log_handler=file_handler)
                # logger.info("execution stopped")
                # logger.removeHandler(file_handler)
                # raise Exception("Unable to get from and to addresses from the email body "+message_subject)
            from_address_domain_in_the_body = "@"+from_address_in_the_body.split("@")[-1]
            print(from_address_domain_in_the_body)
            logger.info("from_address_domain_in_the_body - "+from_address_domain_in_the_body)
            no_of_to_address_in_body =len(to_address_in_the_body)
            logger.info('no_of_to_address_in_body is :'+str(no_of_to_address_in_body))
            message_id_without_sym = re.sub('[^a-zA-Z0-9]', '', message_id)
            root_file_dir = file_directory
            if normal_files_exists:
                #downloaded_files_list = [os.path.abspath(file) for file in os.listdir(root_file_dir) if not (file.lower().endswith('html') or file.lower().endswith('htm'))]
                #logger.info("files in downloaded folder is :")
                # logger.info(downloaded_files_list)
                #if len(downloaded_files_list) != 0:
                        #outlook_graph_apis.forward_message(access_token, message_id, from_and_to_mails_dict['to_email_address'])
                        #cc_mail_ids
                outlook_graph_apis.forward_message(access_token, message_id, ['ranjith.kotha@kanerika.com'], cc_mail_ids)
                    # send_email(username=user_name, password=password, to_recipients=[
                    #     'ranjith.kotha@kanerika.com'], email_subject=from_and_to_mails_dict['subject'],
                    #            email_body="Please find the attachment from the below sender.<br>Sender Name: " +
                    #                       from_and_to_mails_dict['from_email_name'] + '<br>' +
                    #                       'Mail: ' + from_and_to_mails_dict[
                    #                           'from_email_address'] + '<br>Body from sender:<br>' + message_body_html + '<br>Thanks,<br>Decrypt Bot',
                    #            attachment_files_path=root_file_dir)
                    # send_email(username=user_name, password=password, to_recipients=(
                    #          'venkat.sai@kanerika.com','training@kanerika.com'), email_subject=message_subject, email_body=email_body,
                    #                 attachment_files_path=download_directory)
                    # break
                #else:
                    #logger.error(downloaded_files_list)
                    #logger.error("unable to find the downloaded attachments")
                    #raise Exception("Unable to find the downloaded attachments")
            else:
                finished_files = []
                for each_address_index in range(no_of_to_address_in_body):
                    each_to_address = to_address_in_the_body[each_address_index]
                    if each_to_address.lower() in finished_files:
                        continue
                    finished_files.append(each_to_address.lower())
                    logger.info(
                        "Getting password from excel for combination " + from_address_domain_in_the_body + " - " + each_to_address)
                    password_in_excel = get_excel_password(file_name=password_excel_file_path,
                                                           from_domain=from_address_domain_in_the_body,
                                                           to_address=each_to_address)
                    print(each_address_index < (no_of_to_address_in_body))
                    if password_in_excel is not None and each_address_index < no_of_to_address_in_body:
                        # if len(os.listdir(download_directory)) > 0:
                        #     for f in os.listdir(download_directory):
                        #         os.remove(os.path.join(download_directory, f))
                        try:
                            for file in os.listdir(root_file_dir):
                                if file.lower().endswith('.html') or file.lower().endswith('.htm'):
                                    body_Text = marinerfinance_automation.marine_automation(
                                        local_file_path=os.path.join(root_file_dir, file),
                                        download_directory=root_file_dir,
                                        no_of_to_address=no_of_to_address_in_body,
                                        to_address=each_to_address,
                                        password=password_in_excel)
                                    #body_text='asdf'
                                    print(password)
                                    #print(body)
                        except Exception as msg:
                            if str(msg).lower() == "invalid username or password" and each_address_index < (
                                    no_of_to_address_in_body - 1):
                                logger.warn(
                                    "skipping current email address - " + each_to_address + " because of invalid username or password")
                            else:
                                print(msg)
                                logger.error(msg)
                                logger.error("Unable to download the encrypted email attachment file")
                    elif each_address_index >= no_of_to_address_in_body:
                        raise Exception(
                            "Unable to get password from the excel for the combination " + each_to_address + " and " + from_address_domain_in_the_body)
                    else:
                        print(
                            " Skipping the email and moving to next email because unable to get password from the excel for the combination " + each_to_address + " and " + from_address_domain_in_the_body)
                    # break
                downloaded_files_list = [os.path.abspath(file) for file in os.listdir(root_file_dir) if
                                         os.path.isfile(os.path.abspath(file))]
                downloaded_files_list = [file for file in downloaded_files_list if not (file.lower().endswith('.html') or file.lower().endswith('.htm'))]
                logger.info("files in downloaded folder is :")
                logger.info(downloaded_files_list)
                if len(downloaded_files_list) != 0:
                    # send_email(username=user_name, password=password, to_recipients=[
                    #     'ranjith.kotha@kanerika.com'], email_subject=from_and_to_mails_dict['subject'],
                    #            email_body="Please find the attachment from the below sender.<br>Sender Name: " +
                    #                       from_and_to_mails_dict['from_email_name'] + '<br>' +
                    #                       'Mail: ' + from_and_to_mails_dict[
                    #                           'from_email_address'] + '<br>Body from sender:<br>' + message_body_html + '<br>Thanks,<br>Decrypt Bot',
                    #            attachment_files_path=root_file_dir, cc_mails=cc_mail_ids)
                    # from_and_to_mails_dict['to_email_address']

                    send_email(username=user_name, password=password, to_recipients=[
                                            'ranjith.kotha@kanerika.com'], email_subject=from_and_to_mails_dict['subject'],
                               email_body="Please find the attachment from the below sender.<br>Sender Name: " +
                                          from_and_to_mails_dict['from_email_name'] + '<br>' +
                                          'Mail: ' + from_and_to_mails_dict[
                                              'from_email_address'] + '<br>Body from sender:<br>' + body_Text + '<br>Thanks,<br>Decrypt Bot',
                               attachment_files_path=root_file_dir, cc_mails=cc_mail_ids)
                    # send_email(username=user_name, password=password, to_recipients=(
                    #          'venkat.sai@kanerika.com','training@kanerika.com'), email_subject=message_subject, email_body=email_body,
                    #                 attachment_files_path=download_directory)
                    # break
                else:
                    logger.error(downloaded_files_list)
                    logger.error("unable to find the downloaded attachments")
                    raise Exception("Unable to find the downloaded attachments")
            outlook_graph_apis.move_message(access_token, message_id, move_folder)
            # for file in os.listdir(root_file_dir):
            #     os.remove(os.path.join(root_file_dir, file))
            # os.rmdir(root_file_dir)
        # remove here
    logger.info("Job3 Execution completed")
    logger.removeHandler(file_handler)
