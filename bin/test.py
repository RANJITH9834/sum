file_name = r"C:\Users\Venkat\Desktop\Viper PW -Modified worksheet.xlsx"
import pandas as pd

xls = pd.ExcelFile(file_name)
df = pd.read_excel(xls, 'New Password Sheet')
# print(df1)

# This will be used to identify the columns and it's values based on index values

# print(list(df.columns.values))
# print(df.iloc[0,2])

# Filter data column wise

word = "claims1@life-south.com"
# new_df = df[~df["Unnamed: 2"].str.contains(word, na=False)]
# print(new_df)


# new_df = df.query('Unnamed: 2 == "claimsdepartment@life-south.com"')
# print(new_df)


# new_df = df[df["Unnamed: 2"].str.contains(word, na=False)]
# print(new_df)

# new_df  = df.loc[df["Unnamed: 2"] == word]
# print(new_df)

# cities = ["claimsdepartment@life-south.com"]
# new_df = df[df['Unnamed: 2'].isin(cities)]
# print(new_df)

# print(df.loc["Unnamed: 2"])

# df2=df.query(" `Unnamed: 2` == 'claimsdepartment@'")
# print(df2)
# new_df = df.iloc[:5,2]
# print(new_df)
# print(new_df.iloc[11,0])

# new_df1 = df[df['Unnamed: 2'].str.contains("claimsdepartment@life-south.com",na=False)]
# new_df2 = df[df['Unnamed: 1'].str.contains("@marinerfinance.com",na=False)]
# print(new_df2)
# print(new_df2.iloc[0,2])

# print(list(df.columns))
to_address = list(df.columns)
print(to_address)

if word in to_address:
    print(word)
    new_df2 = df[df['Unnamed: 1'].str.contains("@marinerfinance.com", na=False)]
    print(new_df2.loc[0].at[word])
else:
    print("No column with name in sheet New Password Sheet -" + str(word))
