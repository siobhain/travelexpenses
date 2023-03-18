"""
    CCD Travel Expenses Console App
"""
import datetime
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

# emp = SHEET.worksheet('EngineSize')

"""
 Collect trip information from the user
 """

print("Welcome to CCD Travel Expenses - 2023 Log & Approvals")
print("Press L to log trip(s), Press A to approve trip(s), Press H for help")
print("You have chosen to enter trip details, press # to return to 1st level")
print("Please enter trip in the format : Name, Destination, Date in dd/mm")
user_input = input("Enter your trip details Example Tarah, Depot, 23/3/23 \n")
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
    enginesize_ws = SHEET.worksheet('EngineSize')
    name_column = enginesize_ws.col_values(1)
    # first column in EngineSize worksheet contains employee names
    name_column.pop(0)
    # remove element 0 from list which is the column title NAME

    if name_input.lower() not in str(name_column).lower():
        print(f"Invalid Name : {name_input}, Choose from {name_column}")
    else:
        full_name = [
            name for name in name_column if name_input.lower() in name.lower()
            ]
        print(f"Name valid {full_name} - Next check Destinationa then date")
        distance_ws = SHEET.worksheet('Distance')
        destination_column = distance_ws.col_values(1)
        destination_column.pop(0)
        print(destination_column)
        if destination_input.lower() not in str(destination_column).lower():
            print(
                f"Invalid Destination : {destination_input}, \
                    Choose at least 3 letters from {destination_column}"
                )
        else:
            destination = [
                dest for dest in destination_column
                if destination_input.lower() in dest.lower()
            ]
            print("Name & destination valid, now to check date")
            date_input_list = date_input.split("/")
            # puts each item input into a list using , as delimiter
            print(date_input_list)
            try:
                trip_date = datetime.datetime(
                    2023, int(date_input_list[1]), int(date_input_list[0])
                    )
                print(f"date is {trip_date}")
                print(trip_date.strftime("%B"))
                rate_column = enginesize_ws.col_values(3)
                rate_column.pop(0)
                print(name_column, type(name_column))
                print(rate_column, type(rate_column))
                full_name_string = full_name[0]
                destination_string = destination[0]
                print(
                    full_name_string, type(full_name_string),
                    destination_string, type(destination_string)
                     )
                position = name_column.index(full_name_string)
                print(position)
                rate = rate_column[position]
                print(position, rate)
                print("Please ensure this trip you entered is correct:")
                print(
                    f"/t {full_name_string} to {destination_string} on \
                        {(trip_date.strftime('%a %d %b %Y'))}"
                        )
                # user_input = input("Press Y to proceed,
                # or C to cancel & try again")
                print("Press Y to proceed    or    C to cancel & try again")
            except ValueError as e:
                print(
                    f"Invalid date : {e} - {date_input} Enter valid dd/mm"
                    )
