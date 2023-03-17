import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('ccd-travel-expenses')

emp = SHEET.worksheet('EngineSize')
#alldata = emp.get_all_values()
# justgetdata = emp.get_all_records()
# justgetdata = emp.get_values()
# print("get all values")
# print(alldata)
# print("get values")
# print(justgetdata)
name_column = emp.col_values(1)
#while 
# print(firstcol[1])
# print(firstcol[2])
# print(firstcol[3])
# print(firstcol[4])
# firstcol = emp.col_count
# print(firstcol)


"""
 Collect trip information from the user 
"""

print("Welcome to CCD Travel Expenses - 2023 Log & Approvals")
print("Press L to log trip(s), Press A to approve trip(s), Press H for help")
print("You have chosen to enter trip details, press # to return to first level")
print("Please enter trip in the format : Name, Destination, Date in dd/mm/yy ")
user_input = input("Enter your trip details now Example Tarah, Depot, 23/3/23 ")
print("you entered")
print(user_input)

