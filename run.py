import gspread
import datetime

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

# emp = SHEET.worksheet('EngineSize')

"""
 Collect trip information from the user
 """

print("Welcome to CCD Travel Expenses - 2023 Log & Approvals")
print("Press L to log trip(s), Press A to approve trip(s), Press H for help")
print("You have chosen to enter trip details, press # to return to 1st level")
print("Please enter trip in the format : Name, Destination, Date in dd/mm")
user_input = input("Enter your trip details Example Tarah, Depot, 23/3/23 ")
print("you entered")
print(user_input)
print(len(user_input))
# validate trip data that user input

trip_input = user_input.split(",")  # puts into a list using , as delimiter
print(trip_input)

# validate correct number of items

if len(trip_input) != 3:
    raise ValueError(
        f"3 items required : Name,Dest,Date You entered {len(trip_input)}"
        )
else:
    name_input = trip_input[0]
    destination_input = trip_input[1]
    date_input = trip_input[2]
    # verify name
    print(name_input)
    enginesize_ws = SHEET.worksheet('EngineSize')
    name_column = enginesize_ws.col_values(1)
    # first column in EngineSize worksheet contains employee names
    name_column.pop(0)
    # remove element 0 from list which is the column title NAME
    print(name_column)
    print(name_input in str(name_column))
    print("end")
    if name_input not in str(name_column):
        print(f"Invalid Name : {name_input}, Choose from {name_column}")
    else:
        print("Name valid now to check Destinationa then date")
        distance_ws = SHEET.worksheet('Distance')
        destination_column = distance_ws.col_values(1)
        destination_column.pop(0)
        print(destination_column)
        if destination_input not in str(destination_column):
            print(
                f"Invalid Destination : {destination_input}, \
                    Choose at least 3 letters from {destination_column}"
                )
        else:
            print("Name & destination valid, now to check date")
            date_input_list = date_input.split("/")
            # puts each item input into a list using , as delimiter
            print(date_input_list)
            try:
                trip_date = datetime.datetime(
                    2023,int(date_input_list[1]),int(date_input_list[0])
                    )
                print(f"date is {trip_date}")
                print(trip_date.strftime("%B"))
            except ValueError as e:
                print(
                    f"Invalid date : {e} - {date_input} Enter valid dd/mm"
                    )
