import re
from typing import List

import requests
import os
import base64
import json


def get_access_token(app_id, client_secret, directory_id, user_name, password, logger):
    """It will create a access token to access the mail apis"""
    app_id = app_id  # Application Id - on the azure app overview page
    client_secret = client_secret
    directory_id = directory_id
    token_url = "https://login.microsoftonline.com/ " + directory_id + "/oauth2/token"
    logger.info("Getting Access Token")
    logger.info("Access token url - "+token_url)
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
    response_dict = requests.post(token_url, data=token_data, headers=token_headers).json()
    if "error" in response_dict.keys():
        # print(response_dict)
        logger.error("Unable to get access token")
        logger.error(response_dict)
        raise Exception("Unable to get access token")
    else:
        token = response_dict["access_token"]
        refresh_token = response_dict["refresh_token"]
        logger.info("getting access token completed")
        return [token, refresh_token]


def add_attachment(message_id, access_token, content_bytes):
    """This function will add the attachment to the message"""
    attachemnt_url = "https://graph.microsoft.com/v1.0/me/messages/{msg_id}/attachments".format(msg_id=message_id)
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }
    body = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": "Test 1.pdf",
        "contentBytes": content_bytes
    }
    response_dict = requests.post(attachemnt_url, headers=headers, json=body).json()
    # print(response_dict.json())
    if "error" in response_dict.keys():
        print(response_dict)
        raise Exception("Unable to add attachment")
    else:
        return response_dict["id"]


def create_reply_all_email(access_token, message_id):
    """Create reply email to the actual email chain"""
    create_reply_all_url = "https://graph.microsoft.com/v1.0/me/messages/{msg_id}/createReplyAll".format(
        msg_id=message_id)
    headers = {
        "Authorization": "Bearer {token}".format(token=access_token),
        "Content-Type": "application/json"
    }
    print(create_reply_all_url)
    response_dict = requests.post(create_reply_all_url, headers=headers).json()
    # print(response_dict["id"])
    if "error" in response_dict.keys():
        print(response_dict)
        raise Exception("Unable to create reply email")
    else:
        return response_dict["id"]


def update_message(access_token, message_id, message_text):
    """update message to the draft email"""
    create_reply_all_url = "https://graph.microsoft.com/v1.0/me/messages/{msg_id}/createReplyAll".format(
        msg_id=message_id)
    headers = {
        "Authorization": "Bearer {token}".format(token=access_token),
        "Content-Type": "application/json"
    }
    body = {
        "body": {
            "contentType": "text",
            "content": message_text
        }
    }
    # print(create_reply_all_url)
    response_dict = requests.post(create_reply_all_url, headers=headers, json=body).json()
    # print(response_dict["id"])
    if "error" in response_dict.keys():
        print(response_dict)
        raise Exception("Unable to add text to the email body")
    else:
        return response_dict["id"]


def message_ids(token, mail_folder, mails_per_each_run, logger):
    """It will return the message ids which satisfies the filter condition"""
    messages_ids_list = []
    logger.info("Getting message id's from mail folder - "+mail_folder)
    # messages_url = "https://graph.microsoft.com/v1.0/me/mailFolders('{folder}')/messages?$filter=((hasAttachments eq true))&$select=from,subject,id,hasAttachments,body,toRecipients&top={mails_per_each_run}&$orderby=receivedDateTime desc".format(folder=mail_folder, mails_per_each_run=mails_per_each_run)
    #messages_url = "https://graph.microsoft.com/v1.0/me/mailFolders('{folder}')/messages?$filter=((hasAttachments eq true))&$select=from,subject,id,hasAttachments,body,toRecipients&top={mails_per_each_run}".format(folder=mail_folder, mails_per_each_run=mails_per_each_run)
    messages_url = "https://graph.microsoft.com/v1.0/me/mailFolders('{folder}')/messages?$select=from,subject,id,hasAttachments,body,toRecipients&top={mails_per_each_run}".format(
        folder=mail_folder, mails_per_each_run=mails_per_each_run)
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    logger.info("message url - "+messages_url)
    response_dict = requests.get(messages_url, headers=headers).json()
    if "error" in response_dict.keys():
        # print(response_dict)
        logger.error("unable to get message id's")
        logger.error(response_dict)
        raise Exception("Unable to add text to the email body")
    else:
        if len(list(response_dict.get('value'))) > 0:
            for x in response_dict.get('value'):
                message_dict = {}
                message_subject = x.get('subject')
                message_address = x.get('from').get('emailAddress').get('address')
                message_sender_name = x.get('from').get('emailAddress').get('name')
                message_to_addresses = [address['emailAddress']['address'] for address in x.get('toRecipients')]
                message_id = x['id']
                message_type = x.get('body').get('contentType')
                if message_type == "html":
                    message_body = x.get('body').get('content')
                elif message_type == 'text' and x.get('hasAttachments'):
                    message_body = ''
                else:
                    logger.error("Unable to get the body of the email")
                    raise Exception(f"Unable to get the body of the email:{message_id}")
                # message_dict[message_id] = [message_subject, message_address, message_body]
                message_dict[message_id] = [message_subject, message_address, message_body, message_sender_name,
                                            message_to_addresses]
                messages_ids_list.append(message_dict)
                logger.info("getting message id's completed")
            return messages_ids_list
            # print(messages_ids_list)
    return []


def get_attachments(token, mail_folder, message_id, file_directory, logger):
    """This function will download the attachments for the given message id"""
    attachment_type = ["application/octet-stream", "application/pdf"]
    logger.info("Getting attachments from the message id - "+message_id)
    isdir = os.path.isdir(file_directory)
    if not isdir:
        os.makedirs(file_directory)
    # message_id_without_sym = re.sub('[^a-zA-Z0-9]', '', message_id)
    # root_dir = os.path.join(file_directory, message_id_without_sym)
    # if not os.path.exists(root_dir):
    #     os.makedirs(root_dir)
    # if len(os.listdir(file_directory)) > 0:
    #     for f in os.listdir(file_directory):
    #         os.remove(os.path.join(file_directory, f))
    Attachments_url = f"https://graph.microsoft.com/v1.0/me/mailFolders('{mail_folder}')/messages/" + message_id + "/attachments"
    logger.info("Attachment url - "+Attachments_url)
    # print(Attachments_url)
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    response_dict = requests.get(Attachments_url, headers=headers).json()
    if "error" in response_dict.keys():
        # print(response_dict)
        logger.error("unable to get attachments")
        logger.error(response_dict)
        raise Exception("Unable to get response from attachment api")
    else:
        counter = 0
        normal_files_present = False
        for y in response_dict['value']:
            # print(y['contentType'])
            if ((y['contentType'] in attachment_type or str(y['contentType']).lower().startswith('image/')) or
                (y['contentType'] is None and y['name'] == '' and y['size'] > 1)) and y['isInline'] == False:
                if not (y['name'].lower().endswith('.html') or y['name'].lower().endswith('htm')):
                    normal_files_present = True
                counter = counter + 1
        if counter > 0:
            if normal_files_present:
                return normal_files_present
            for y in response_dict['value']:
                if (y['contentType'] in attachment_type or str(y['contentType']).lower().startswith('image/')) and y['isInline'] == False:
                    try:
                        modified_filename = str(y['name'])
                        file_name = os.path.join(file_directory, modified_filename)
                        if not (modified_filename.lower().endswith('.html') or modified_filename.lower().endswith('htm')):
                            normal_files_present = True
                        print(file_name)
                        f = open(file_name, "w+b")
                        f.write(base64.b64decode(y['contentBytes']))
                    except Exception as msg:
                        print(msg)
                        logger.error("unable to download the attachments from response")
                        logger.error(msg)
                        raise Exception("unable to download the attachments from response")
                    else:
                        f.close()
                    # print("attachment downloaded successfully")
                    logger.info("attachment downloaded successfully")
                    # return file_name
            return normal_files_present
        else:
            raise Exception("unable to automate this file")

def move_message(token, message_id, move_folder):
    move_url = "https://graph.microsoft.com/v1.0/me/messages/{messageId}/move".format(messageId=message_id)
    headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
    move_data = {"destinationId": "{move_folder}".format(move_folder=move_folder)}
    move_data = json.dumps(move_data)
    response_dict = requests.post(move_url, data=move_data, headers=headers).json()
    if "error" in response_dict.keys():
        print(response_dict)
        raise Exception("Unable to move the mail")
    else:
        print("message moved successfully")


def forward_message(token: str, message_id: str, to_addresses: List, cc_mail_ids: List ):
    url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}/forward'

    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    forward_data = {
        "comment": "",
        "toRecipients": [{"emailAddress": {"name": to_address,
                                           "address": to_address}} for to_address in to_addresses],
        "cc": [{"email": {"name": cc_mail_ids,
                                           "address": cc_mail_ids}} for cc_mail_ids in cc_mail_ids]
    }
    print(forward_data)
    response = requests.post(url, headers=headers, data=json.dumps(forward_data))
    if response.status_code != 202:
        raise Exception("Unable to forward the mail")
    print('successfully forward the mail')
