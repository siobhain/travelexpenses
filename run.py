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

def get_trip_data():
"""
    Ask user to enter 3 items to log the trip
"""
    print("You have chosen to enter trip details")
    print("Please enter trip in the format : Name, Destination, Date in dd/mm")

    while true:
        user_input = input(
            "Enter your trip details Example tarah, depo, 23/3 \n"
            )
        trip_input = user_input.split(",")  # Into list using , as delimiter
        if len(trip_input) != 3:
            raise ValueError(
                f"3 items required, You entered {len(trip_input)}"
                )
            else:
                if validate_trip_data(trip_input):
                    print("Logging Trip")
                    break


def validate_trip_data(trip_input)

"""
    Three items input for trip
    NAME - needs to match name in spreadsheet
    DESTINATION - needs to match destination in spreadsheet
    DATE - needs to be valid date 

"""

    name_input = trip_input[0]
    destination_input = trip_input[1]
    date_input = trip_input[2]
    # verify name
    is_name_in_spreadsheet(name_input,'EngineSize')
    is_data_in_spreadsheet(destination_input,'Distance')
    

    enginesize_ws = SHEET.worksheet('EngineSize')
    name_column = enginesize_ws.col_values(1)
    # first column in EngineSize worksheet contains employee names
    name_column.pop(0)
    # remove element 0 from list which is the column title NAME

    if name_input.lower() not in str(name_column).lower():

"""
 Collect trip information from the user

"""

def is_data_in_spreadsheet

print("Welcome to CCD Travel Expenses - 2023 Log & Approvals")
print("Press L to log trip(s), Press A to approve trip(s), Press H for help")
# print("You have chosen to enter trip details, press # to return to 1st level")
# print("Please enter trip in the format : Name, Destination, Date in dd/mm")
# user_input = input("Enter your trip details Example Tarah, Depot, 23/3/23 \n")

# validate trip data that user input

#trip_input = user_input.split(",")  # puts into a list using , as delimiter

# validate correct number of items
# need a while loop for continuous entry

get_trip_data():

if len(trip_input) != 3:
    raise ValueError(
        f"3 items required : Name, Dest, Date You entered {len(trip_input)}"
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
        #input again
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
            try:
                trip_date = datetime.datetime(
                    2023, int(date_input_list[1]), int(date_input_list[0])
                    )
                rate_column = enginesize_ws.col_values(3)
                rate_column.pop(0)
                full_name_string = full_name[0]
                destination_string = destination[0]
                print("Please ensure this trip you entered is correct:")
                print(
                    f"\t{full_name_string} to {destination_string} on "
                    f"{(trip_date.strftime('%a %d %b %Y'))}"
                    )
                # user_input = input("Press Y to proceed,
                # or C to cancel & try again")
                print("Press Y to proceed    or    C to cancel & try again")
                position = name_column.index(full_name_string)
                rate = rate_column[position]
                position = destination_column.index(destination_string)
                distance_column = distance_ws.col_values(2)
                distance_column.pop(0)
                print(distance_column)
                distance = distance_column[position]
                print(distance)
                amount = round(float(rate) * int(distance))
                print(amount)
                print(
                    datetime.datetime.now(), full_name_string,
                    trip_date, amount
                    )
                travel_expenses_ws = SHEET.worksheet('TravelExpenses')
                travel_expenses_ws.append_row(
                    [(datetime.datetime.now()).strftime('%a %d %b %Y'),
                     full_name_string, (trip_date.strftime('%a %d %b %Y')),
                     amount]
                    )
                print("Updated worksheet")
            # this except is only true is 1st try stmt fails
            except ValueError as e:
                print(
                    f"Invalid date : {e} - {date_input} Enter valid dd/mm"
                    )
