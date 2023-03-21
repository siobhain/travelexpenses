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

    while True:
        user_input = input(
            "Enter your trip details Example tarah, depo, 13/3 \n"
            )
        trip_input = user_input.split(",")  # Into list using , as delimiter
        if len(trip_input) != 3:
            raise ValueError(
                f"3 items required, You entered {len(trip_input)}"
                )
        else:
            if validate_trip_data(trip_input):
                print("Logging Trip.Put rest of code to update worksheet")
                break
    return trip_input   


def validate_trip_data(trip_input):
    """
    Three items input for trip
    NAME - needs to match name in spreadsheet
    DESTINATION - needs to match destination in spreadsheet
    DATE - needs to be valid date 

    """
    name_input = trip_input[0]
    destination_input = trip_input[1]
    date_input = trip_input[2]
    date_input_list = date_input.split("/")
    
    if verify_data(name_input, 'EngineSize'): 
        if verify_data(destination_input, 'Distance'):
            try:
                trip_date = datetime.datetime(
                    2023, int(date_input_list[1]), int(date_input_list[0])
                    )
                print(trip_date)
            except ValueError as e:
                print(f"{date_input} is Invalid : {e}")
                return False
        else:
            print(f"Invalid Destination : {destination_input}")
            return False
    else:
        print(f"Invalid Name : {name_input}")
        return False
    return True
            

"""
 Collect trip information from the user

"""


def verify_data(data_input, worksheet):
    """
    This function check if data is in worksheet, used for employee name 
    and destination aa both in first column of spreadsheet
    """
    data_worksheet = SHEET.worksheet(worksheet)
    data_column = data_worksheet.col_values(1)
    # first column in EngineSize worksheet contains employee names
    data_column.pop(0)
    # remove element 0 from list which is the column title NAME

    if data_input.lower() in str(data_column).lower():
        print(f"found item {data_input}")
        return True
    else:
        print(f"Choose from {data_column}")
        return False


def create_trip_record(trip_input):
    """
    Expand the data/
    perform processing before entry to spreadsheet
    Needs to be in following order 
    STATUS,	SUBMITDATE,	TRAVELDATE,	NAME, DESTINATION, AMOUNT
    """
    # get full name and destination strings

    trip_name = expand_data(trip_input[0], 'EngineSize')
    trip_destination = expand_data(trip_input[1], 'Distance')
    date_input_list = (trip_input[2]).split("/")
    trip_date = datetime.datetime(
        2023, (int((date_input_list[1]))), (int((date_input_list[0])))
        ).strftime('%a %d %b %Y')
    today = (datetime.datetime.now()).strftime('%a %d %b %Y')
    print(today, trip_date, trip_name, trip_destination)
    
    #trip_record = list("PENDING", today_date,trip_date,trip_name,trip_destination,trip_amount)

    rate_in_cent_per_km = get_milage_rate(trip_name)
    distance = get_distance_in_km(trip_destination)
    amount = float(rate_in_cent_per_km) * int(distance)

    print(today, trip_date, trip_name, trip_destination, rate_in_cent_per_km, distance, amount)


def get_milage_rate(name):
    """
    This function returns the milage rate in cent per kilometer for the name sent in
    the EngineSize worksheet has column headings for the employees that can claim travel
    NAME, ENGINE SIZE cc,Allowance per Km
    There is a row for each employee that can claim travel expanses
    Open woksheet, find index of employee to get rate for that employee
    """
    enginesize_ws = SHEET.worksheet('EngineSize')
    employees_column = enginesize_ws.col_values(1)
    print(employees_column)
    rate_column = enginesize_ws.col_values(3)
    print(rate_column)
    name_string = name[0]
    row_number = employees_column.index(name_string)
    print("in milage rate")
    print(rate_column,row_number)
    return rate_column[row_number]
    
def get_distance_in_km(destination):
    """
    This function uses the destination send to it to #
    find the distance of said destination from spreadsheet
    """
    distance_ws = SHEET.worksheet('Distance')
    destination_column = distance_ws.col_values(1)
    print(destination_column)
    distance_column = distance_ws.col_values(2)
    print(distance_column)
    destination_string = destination[0]
    row_number = destination_column.index(destination_string)
    print(f"{destination_string} is at Row {row_number} in {destination_column}")
    return distance_column[row_number]









"""
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

"""


def expand_data(data_input, worksheet):
    """
    This function takes the user input shorthand/substring
    and returns the full item/longhand stored in spreadsheet
    """
    data_worksheet = SHEET.worksheet(worksheet)
    data_column = data_worksheet.col_values(1)

    full_data = [
        item for item in data_column if data_input.lower() in item.lower()
        ]
    print(f"Expand {data_input} to {full_data}")
    return full_data


print("Welcome to CCD Travel Expenses - 2023 Log & Approvals")
print("Press L to log trip(s), Press A to approve trip(s), Press H for help")
# print("You have chosen to enter trip details, press # to return to 1st level")
# print("Please enter trip in the format : Name, Destination, Date in dd/mm")
# user_input = input("Enter your trip details Example Tarah, Depot, 23/3/23 \n")

# validate trip data that user input

# trip_input = user_input.split(",")  # puts into a list using , as delimiter

# validate correct number of items
# need a while loop for continuous entry

trip_data_input = get_trip_data()
# All data entered is valid and verified, let expand it
create_trip_record(trip_data_input)
#trip_name = expand_data(trip_data_input[0], 'EngineSize')
#trip_destination = expand_data(trip_data_input[1],'Distance')
# Create Trip record to be added to spreadsheet



"""
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
"""
