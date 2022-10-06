from selenium import webdriver
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import wait_until_attachment_downloaded
from selenium.common.exceptions import NoSuchElementException,TimeoutException

from bin.getPasswordFromExcel import get_excel_password


def login(driver, password):
    # Wait and Get To_email(UserName)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"emailTo\"]")))
    print(driver.find_element(By.XPATH, "//*[@id=\"emailTo\"]").text)
    # Wait and Type Password
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"passwordInput1\"]")))
    password_element = driver.find_element(By.XPATH, "//*[@id=\"passwordInput1\"]")
    password_element.send_keys(password)
    # Wait and Click Open Online Button
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//*[@id='openButtonLocation']")))
    submit_button = driver.find_element(By.XPATH, "//*[@id='openButtonLocation']")
    submit_button.click()
    try:
        # Check if the password correct or not
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//*[@id='passMsg']/span")))
        incorrect_element = driver.find_element(By.XPATH, "//*[@id='passMsg']/span")
        if incorrect_element.text.lower() == "Incorrect email address or password. Please try again.".lower():
            raise Exception("Invalid UserName or Password")
    except (NoSuchElementException, TimeoutException):
        print("successfully logged in")


def marine_automation(local_file_path, download_directory, no_of_to_address, password_excel_file_path,
                      from_address_domain_in_the_body):
    """This Function will do the web automation """

    # Getting Chrome Instance
    op = webdriver.ChromeOptions()

    # Adding arguments to the chrome
    op.add_argument("--enable-webgl-developer-extensions")
    op.add_argument("--enable-webgl-draft-extensions")

    # This method will help us to download the pdf files into particular folder
    op.add_experimental_option('prefs', {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })

    # Creating driver object with required arguments
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=op)

    # opening encrypted email
    driver.get(local_file_path)

    # maximizing the window
    driver.maximize_window()
    time.sleep(10)

    if no_of_to_address > 1:
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//*[@id='toSelect']")))
        username_dropdown = driver.find_element(By.XPATH, "//*[@id='toSelect']")
        option_list_elements = username_dropdown.find_elements(By.XPATH, ".//*")
        found = True
        for each_option in option_list_elements:
            to_address = each_option.text
            if to_address == '' or to_address == 'Address not listed':
                continue
            each_option.click()
            time.sleep(5)
            # Click on Submit button
            submit_element = driver.find_element(By.XPATH, "//*[@id='text_buttonSubmit']")
            submit_element.click()
            password = get_excel_password(file_name=password_excel_file_path,
                                          from_domain=from_address_domain_in_the_body,
                                          to_address=to_address)
            try:
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "authFrame")))
                driver.switch_to.frame("authFrame")
                login(driver, password)
                found = False
                break
            except:
                back = driver.find_element(By.XPATH, "//*[@id='wrongAddressLink']")
                back.click()
                time.sleep(5)
                driver.switch_to.default_content()
        if found:
            raise Exception("Invalid UserName or Password")
    else:
        # Switching to iframe to access inner elements
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "authFrame")))
        driver.switch_to.frame("authFrame")
        to_address = driver.find_element(By.XPATH, "//*[@id='emailTo']").text
        password = get_excel_password(file_name=password_excel_file_path,
                                      from_domain=from_address_domain_in_the_body,
                                      to_address=to_address)
        try:
            login(driver, password)
        except:
            raise Exception("Invalid UserName or Password")

    # Switching Out from Iframe to Default
    driver.switch_to.default_content()
    print(driver.current_url)
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, "WordSection1")))
    body = driver.find_element_by_class_name('WordSection1')
    body_text = None
    if body:
        body_text = body.text

    # Wait and Get Subject From the Email
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[@id='subjectBarHeader']")))
    subject = driver.find_element(By.XPATH, "//*[@id='subjectBarHeader']").text
    print(subject)

    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[@id='bodycontent']/div")))
    body = driver.find_element(By.XPATH, "//*[@id='bodycontent']/div").text
    print(body)

    # Wait and Download the Attachments
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id='srform']/table/tbody/tr/td/table/tbody/tr[3]/td/table")))
    attachment_path_table = driver.find_elements(By.XPATH,
                                                 "//*[@id='srform']/table/tbody/tr/td/table/tbody/tr[3]/td/table")
    # print((attachment_path_table))
    attachments_found = False
    for table_record_element in attachment_path_table:
        WebDriverWait(driver,60).until(EC.element_to_be_clickable(table_record_element))
        table_definition_list = table_record_element.find_elements(By.TAG_NAME, "tr")
        print(table_definition_list[-1].tag_name)
        for each_element in table_definition_list[-1].find_elements(By.XPATH, ".//*"):
            # print(each_element.tag_name)
            if each_element.tag_name == 'a':
                print("file-name")
                attachment_file_name = each_element.text
                print(attachment_file_name)
                # print(attachment_file_name)
                # if not attachment_file_name.lower().endswith('.pdf'):
                #     resp = requests.get(each_element.get_attribute('href'))
                #     if resp.status_code == 200:
                #         with open(f'{download_directory}/{attachment_file_name}', 'wb') as file:
                #             file.write(resp.content)
                #     else:
                #         print("unable to get the image")
                # else:
                each_element.click()

                time.sleep(10)
                attachments_found = True

    if not attachments_found:
        print("No attachments found")
    else:
        print("Attachments Found")
    # attachment_file_path = os.path.join(download_directory, attachment_file_name)
    response = wait_until_attachment_downloaded.wait_for_download(folder_path=download_directory)
    if response is not None:
        driver.close()
        raise Exception("File downloading time is > 5 min's for file - " + response)
    else:
        driver.close()
    print("done")
    #return body
    return body_text.replace('\n', '<br>')

    #WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[@id='bodycontent']/div")))
    #body = driver.find_element(By.XPATH, "//*[@id='bodycontent']/div").text
    #print(body)


# attachment_path = "C:\\Users\\Venkat\\Desktop\\decryptedEmails\\securedoc_20220601T104744.html"
# download_directory = "C:\\Users\\Venkat\\Desktop\\decryptedEmailAttachments"
# no_of_to_address_in_body = 2
# each_to_address = 'claims@life-south.com'
# password_in_excel = "CiscoClm205"
# marine_automation(local_file_path=attachment_path, download_directory=download_directory, no_of_to_address=no_of_to_address_in_body, to_address=each_to_address, password=password_in_excel)
