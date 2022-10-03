import os
import datetime
import time


def latest_download_file(folder_path):
    path = folder_path
    os.chdir(path)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    newest = files[-1]
    return newest


# folder_path = "C:\\Users\\Venkat\\Desktop\\decryptedEmailAttachments"
#
# newest_file = latest_download_file(folder_path=folder_path)
# print(newest_file)



def wait_for_download(folder_path):
    file_ends = "crdownload"
    start_time = datetime.datetime.now()
    while "crdownload" == file_ends:
        time.sleep(1)
        newest_file = latest_download_file(folder_path)
        if "crdownload" in newest_file:
            file_ends = "crdownload"
            current_time = datetime.datetime.now()
            time_diff = (current_time - start_time).total_seconds() / 60.0
            if time_diff >= 1.0:
                print("time exceeded")
                raise Exception("Time Exceeded 2 min's unable to download file")
        else:
            return None
