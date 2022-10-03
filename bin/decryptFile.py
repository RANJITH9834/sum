import pathlib
import msoffcrypto

url = pathlib.Path("C:\\Users\\Venkat\\Desktop\\testExcelFiles")
excel_files = list(url.glob('*.xlsx'))
print(excel_files)


def unlock(filename, passwd, output_folder):
    temp = open(filename, 'rb')
    excel = msoffcrypto.OfficeFile(temp)
    excel.load_key(passwd)
    out_path = pathlib.Path(output_folder)
    if not out_path.exists():
        out_path.mkdir()

    with open(str(out_path/filename.name), 'wb') as f:

        excel.decrypt(f)
    temp.close()

unlock(filename=excel_files[0],passwd="Kanerika",output_folder="C:\\Users\\Venkat\\Desktop\\testOutputFolder")