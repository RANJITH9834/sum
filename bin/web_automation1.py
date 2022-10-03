import traceback
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import logging
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager


class FlinscoFileUpload:

    def __init__(self, upload_file_path, logger, error_files_download_path):
        self.fccms_url = "https://fccms.uat.priv.life-south.com/Para/Account/Login.aspx"
        self.fccms_username = "aditya"
        self.fccms_password = "Indi@2022!"
        self.upload_file_path = upload_file_path
        self.status = None
        self.file_name = None
        self.success_records = None
        self.failure_records = None
        self.total_records = None
        self.error_message = None
        self.created_date = None
        self.created_by = None
        self.error_filepath = None
        self.upload_file_path = upload_file_path
        self.upload_success_flag = True
        self.logger = logger
        self.DOWNLOADS_FOLDER_PATH = error_files_download_path

    def web_automation(self):
        self.logger.info("Opening Chrome")
        op = webdriver.ChromeOptions()
        op.add_argument("--incognito")
        self.logger.info("Installing chrome driver")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=op)
        action = ActionChains(driver)
        self.logger.info("opening site - " + self.fccms_url)
        driver.get(self.fccms_url)
        self.logger.info("Entering username")
        # Entering the username
        username_element = driver.find_element(By.ID, "LoginUser_UserName")
        username_element.send_keys(self.fccms_username)
        self.logger.info("ENtering password")
        # Entering the password
        password_element = driver.find_element(By.ID, "LoginUser_Password")
        password_element.send_keys(self.fccms_password)
        self.logger.info("Click on Login")
        # Clicking on the login button
        login_button_element = driver.find_element(By.ID, "LoginUser_LoginButton")
        action.click(on_element=login_button_element).perform()

        # Clicking on the Active Knight image button
        self.logger.info("Clicking on the Active Knight image button")
        auto_knight_image_element = driver.find_element(By.ID, "uxAK")
        action.click(on_element=auto_knight_image_element).perform()

        # Clicking on the Configuration tab
        self.logger.info("Clicking on Configuration tab")
        configuration_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"ctl00_uxRibbonTab\"]/div/ul/li[2]/a/span/span/span")))
        action.click(on_element=configuration_element).perform()

        # Clicking on the Import Data image button
        self.logger.info("Clicking on Import Data image button")
        import_data_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"uxImportDataAction\"]/span/span/span/img")))
        action.click(on_element=import_data_element).perform()

        # Clicking on the data type dropdown
        self.logger.info("Click on DataType DropDown")
        data_type_dropdown_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"ctl00_Body_uxSelectDataType\"]/table")))
        action.click(on_element=data_type_dropdown_element).perform()

        # Getting the list of dropdown options
        self.logger.info("Get list of DropDown Options")
        data_type_dropdown_list_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"ctl00_Body_uxSelectDataType_DropDown\"]/div/ul")))

        # Clicking on the 'Membership Info' dropdown option
        self.logger.info("CLick on Membership INfo")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "li")))
        dropdown_options = data_type_dropdown_list_element.find_elements(By.TAG_NAME, "li")
        print(len(dropdown_options))
        for option in dropdown_options:
            dropdown_label = option.text
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(option))
            if dropdown_label.strip().lower() == "Membership Info".lower():
                action.click(on_element=option).perform()
                break

        # Wait for 3 minutes
        time.sleep(5)

        # Getting the old processed record's table before uploading the file

        old_latest_created_datetime = ""
        old_processed_table_record_dict_by_user_and_created_date = self.get_records_from_table(driver)
        if len(old_processed_table_record_dict_by_user_and_created_date) > 0:
            sorted_old_processed_table_record_list_by_user_and_created_date = sorted(
                old_processed_table_record_dict_by_user_and_created_date.items(),
                key=lambda x: datetime.strptime(x[0], '%m/%d/%Y %H:%M:%S %p'), reverse=True)
            old_latest_created_datetime = sorted_old_processed_table_record_list_by_user_and_created_date[0][0]
            print("Created by for the latest record before file upload: ", old_latest_created_datetime)
            self.logger.info("Created by for the latest record before file upload: " + str(old_latest_created_datetime))

        # Uploading the target file
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"ctl00_Body_uxUploadTemplatefile0\"]")))
        upload_file_element = driver.find_element(By.XPATH, "//*[@id=\"ctl00_Body_uxUploadTemplatefile0\"]")
        logging.info("File Path: ", self.upload_file_path)
        upload_file_element.send_keys(self.upload_file_path)
        self.logger.info("Upload file path - " + str(self.upload_file_path))

        time.sleep(5)

        # Clicking on Process button after uploading the file
        process_button_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"ctl00_Body_uxSaveDocument_input\"]")))
        action.click(on_element=process_button_element).perform()
        self.logger.info("Clicking on process button after uploading the file")
        time.sleep(17)

        # Getting the text from the alert pop up after file upload
        try:
            alert_element_1 = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//tr[@class=\"rwContentRow\"]")))
            alert_text = alert_element_1.find_element(By.CLASS_NAME, "rwDialogText").text
            print("Pop Up Message: ", alert_text)
            self.logger.info("Pop Up Message" + str(alert_text))
            self.error_message = alert_text
            alert_ok_element = alert_element_1.find_element(By.CLASS_NAME, "rwInnerSpan")
            action.click(on_element=alert_ok_element).perform()
        except:
            print("The file is uploaded successfully")
            self.logger.info("File is uploaded successfully")
        time.sleep(7)

        # Getting the new processed record's table after uploading the file
        self.upload_success_flag = True
        new_processed_table_record_dict_by_user_and_created_date = self.get_records_from_table(driver)
        if len(new_processed_table_record_dict_by_user_and_created_date) > 0:
            sorted_new_processed_table_record_list_by_user_and_created_date = sorted(
                new_processed_table_record_dict_by_user_and_created_date.items(),
                key=lambda x: datetime.strptime(x[0], '%m/%d/%Y %H:%M:%S %p'), reverse=True)
            new_latest_created_datetime = sorted_new_processed_table_record_list_by_user_and_created_date[0][0]
            print("Created by for the latest record after file upload: ", new_latest_created_datetime)

            if new_latest_created_datetime == old_latest_created_datetime:
                self.upload_success_flag = False
                self.logger.info("new_latest_created_datetime == old_latest_created_datetime")
                self.logger.info("upload_success_flag is - " + str(self.upload_success_flag))
            else:
                table_record_with_latest_created_datetime = new_processed_table_record_dict_by_user_and_created_date[
                    new_latest_created_datetime]
                table_definition_list = table_record_with_latest_created_datetime.find_elements(By.TAG_NAME, "td")
                self.file_name = table_definition_list[1].text
                self.status = table_definition_list[2].text
                self.success_records = table_definition_list[3].text
                self.failure_records = table_definition_list[4].text
                self.total_records = table_definition_list[5].text
                self.created_date = table_definition_list[6].text
                self.created_by = table_definition_list[7].text
                self.error_filepath = os.path.join(self.DOWNLOADS_FOLDER_PATH, table_definition_list[8].text.strip())

                # Downloading the error file
                if int(self.failure_records) > 0:
                    error_file_element = table_definition_list[8].find_element(By.TAG_NAME, "a")
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(error_file_element))
                    action.click(on_element=error_file_element).perform()
                    self.logger.info("downloading the error file")

                print(self.file_name)
                print(self.status)
                print(self.success_records)
                print(self.failure_records)
                print(self.total_records)
                print(self.created_date)
                print(self.created_by)
                print(self.error_filepath)

        # Clicking on Logout link
        logout_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"LoginView1_HeadLoginStatus\"]")))
        action.click(on_element=logout_element).perform()

        time.sleep(5)
        driver.close()

    def get_records_from_table(self, driver):
        # Getting the new processed record's table after uploading the file
        processed_records_table_body_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table[@id=\"ctl00_Body_uxTemplateList_ctl00\"]/tbody")))
        # processed_records_table_body_element = driver.find_element(By.XPATH, "//table[@id=\"ctl00_Body_uxTemplateList_ctl00\"]/tbody")
        processed_table_record_list_elements = processed_records_table_body_element.find_elements(By.TAG_NAME, "tr")

        # Getting the success_records, failure_records and total_records if the filename matches the uploaded file name
        processed_table_record_list_by_user_and_created_date = {}
        for table_record_element in processed_table_record_list_elements:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(table_record_element))
            table_definition_list = table_record_element.find_elements(By.TAG_NAME, "td")
            created_datetime = table_definition_list[6].text
            created_by = table_definition_list[7].text
            if created_by == self.fccms_username:
                processed_table_record_list_by_user_and_created_date[created_datetime] = table_record_element

        return processed_table_record_list_by_user_and_created_date


# flinscoFileUpload = FlinscoFileUpload("D:\\Fotegra\\MOTOR CLUB\\Flinsco\\Output Files\\ims-Fortega-5-18-22(1)-May-18-2022-13-20-00.xlsx")
# try:
#     flinscoFileUpload.web_automation()
# except Exception as e:
#     logging.error(traceback.format_exc())
#     print(flinscoFileUpload.status)


local_file_path = "C:\\Users\\Venkat\\Downloads\\securedoc_20220601T104744.html"
op = webdriver.ChromeOptions()
op.add_argument("--enable-webgl-developer-extensions")
op.add_argument("--enable-webgl-draft-extensions")
# This method will help us to download the pdf files into particular folder
op.add_experimental_option('prefs', {
    "download.default_directory": "C:\\Users\\Venkat\\Desktop\\decryptedEmailAttachments",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=op)
action = ActionChains(driver)
# opening encrypted email
driver.get(local_file_path)
# maximizing the window
driver.maximize_window()
time.sleep(10)
# Switching to iframe to access inner elements
# driver.switch_to.frame("authFrame")
# Wait and Get To_email(UserName)
# WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//select[@value='claims@fortegra.com")))
username_dropdown = driver.find_element(By.XPATH, "//*[@id='toSelect']")
option_list_elements = username_dropdown.find_elements(By.XPATH, ".//*")
# print(option_list_elements)
for each_option in option_list_elements:
    if each_option.text.lower() == 'claims@fortegra.com':
        each_option.click()
time.sleep(5)
submit_element = driver.find_element(By.XPATH, "//*[@id='text_buttonSubmit']")
submit_element.click()
# # Wait and Type Password
# WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"passwordInput1\"]")))
# password_element = driver.find_element(By.XPATH, "//*[@id=\"passwordInput1\"]")
# password_element.send_keys("CiscoCD2020")
# # Wait and Click Open Online Button
# WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='openButtonLocation']")))
# submit_button = driver.find_element(By.XPATH, "//*[@id='openButtonLocation']")
# submit_button.click()
# # Switching Out from Iframe to Default
# driver.switch_to.default_content()
# print(driver.current_url)
# # Wait and Get Subject From the Email
# WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='subjectBarHeader']")))
# subject = driver.find_element(By.XPATH,"//*[@id='subjectBarHeader']").text
# print(subject)
# # Wait and Download the Attachments
# WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='srform']/table/tbody/tr/td/table/tbody/tr[3]/td/table")))
# attachment_path_table = driver.find_elements(By.XPATH, "//*[@id='srform']/table/tbody/tr/td/table/tbody/tr[3]/td/table")
# # print((attachment_path_table))
# attachments_found = False
# for table_record_element in attachment_path_table:
#     WebDriverWait(driver, 20).until(EC.element_to_be_clickable(table_record_element))
#     table_definition_list = table_record_element.find_elements(By.TAG_NAME, "tr")
#     print(table_definition_list[-1].tag_name)
#     for each_element in table_definition_list[-1].find_elements(By.XPATH, ".//*"):
#         # print(each_element.tag_name)
#         if each_element.tag_name == 'a':
#             each_element.click()
#             attachments_found = True
# if attachments_found == False:
#     print("No attachments found")
# else:
#     print("Attchments Found")
# time.sleep(10)
# driver.close()
# print("done")
