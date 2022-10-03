from importlib.resources import contents
from pathlib import Path
from bs4 import BeautifulSoup
import re
#
# file_path = "C:\\Users\\Venkat\\Desktop\\New Text Document.txt"
# contents = Path(file_path).read_text()


def get_all_email_address(contents):
    soup = BeautifulSoup(contents, "html.parser")
    all_text = soup.text.lower()
    emails = re.findall(r"from:.+[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", all_text)
    if not emails:
        return {'from_email_address': '', 'to_email_address': None,
            'from_email_name': None, 'subject': None}
    # print(emails)
    from_email = emails[0].split("sent")[0]
    # print(from_email)
    from_email_name = re.search(r"from: ([a-zA-Z0-9 ]+) <[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+>", soup.text,
                                flags=re.I).groups(1)
    from_email_name = from_email_name[0] if from_email_name else ''
    from_email_address = re.search(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", from_email)
    # print(from_email_address[0])
    to_address = emails[0].split("to")[1]
    subject = soup.find(text=re.compile('Subject:')).parent.next_sibling.text
    if "cc:" in to_address:
        to_address = to_address.split("cc")[0]
    else:
        to_address = to_address.split("subject")[0]
    # print(to_address)
    to_email_address = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", to_address)
    # print(x)
    return {'from_email_address': from_email_address[0], 'to_email_address': to_email_address,
            'from_email_name': from_email_name, 'subject': subject}

# print(soup.text)
# print(soup.prettify())
# all_text = ''
# texts = soup.find_all('p')
# for text in texts:
#     # print(text.get_text())
#     all_text = all_text+"\n"+text.get_text() 
# print(all_text) 
# emails = get_all_email_address(contents=contents)
# print(emails)
