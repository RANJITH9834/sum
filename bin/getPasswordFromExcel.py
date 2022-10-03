import pandas as pd


def get_excel_password(file_name, from_domain, to_address, sheet_name='New Password Sheet'):
    xls = pd.ExcelFile(file_name)
    df = pd.read_excel(xls, sheet_name)
    to_address_in_excel = list(df.columns)
    print(to_address_in_excel)
    if to_address in to_address_in_excel:
        print(to_address)
        new_df2 = df[df['Unnamed: 1'].str.contains(from_domain, na=False)]
        required_password = new_df2.loc[0].at[to_address]
        return required_password
    else:
        print("No column with name in sheet New Password Sheet -" + str(to_address))
        return None

