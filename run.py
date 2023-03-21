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

def get_main_menu():
    """
    This function asks user to chose and 
    """

    main_menu = ''' 
        1) Enter 1 to Log a trip for travel expenses
        2) Enter 2 to Generate a travel expenses report
        3. Enter 3 to Approve travel expenses
        4. Enter 4 to Exit
        '''
    print(main_menu)
    user_input = ""
    while user_input != '4':
        try:
            user_input = input("Enter 1, 2, 3 or 4 \n")
            if user_input == "":
                raise ValueError(" Input is blank ")
            elif not user_input.isnumeric():
                raise ValueError(" Numeric value only ")
            elif int(user_input) > 0 and int(user_input) < 5:
                pass
            else:
                raise ValueError(" Invalid numeric ")
        except ValueError as e:        
            print(f" {e}, Please try again. \n")


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
        try:
            trip_input = user_input.split(",")  # Into list using , as delimiter
            if user_input == "":
                raise ValueError("Input is blank, ")
            elif len(trip_input) != 3:
                raise ValueError(
                    f"3 items required, You entered {len(trip_input)}"
                    )
            else:
                if validate_trip_data(trip_input):
                    print("Trip accepted, Logging details")
                    break
        except ValueError as e:
            print(f"Invalid Data: {e}, Please try again. \n")

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
                trip_date = datetime.date(
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
    trip_date = datetime.date(
        2023, (int((date_input_list[1]))), (int((date_input_list[0])))
        ).strftime('%a %d %b %Y')
    today = (datetime.date.today()).strftime('%a %d %b %Y')
    print(today, trip_date, trip_name, trip_destination)
    
    #trip_record = list("PENDING", today_date, trip_date,trip_name, trip_destination, trip_amount)

    rate_in_cent_per_km = get_milage_rate(trip_name)
    distance = get_distance_in_km(trip_destination)
    amount = round(((float(rate_in_cent_per_km) * int(distance))/100), 2)
    trip_record = list(("PENDING", today, trip_date, trip_name[0], trip_destination[0], amount))
    print(today, trip_date, trip_name, trip_destination, rate_in_cent_per_km, distance, amount)
    print(trip_record)
    return trip_record

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

def submit_trip_record(trip_details):
    """
    This function updates the TravelExpenses worksheet with trip
    entered by the user
    """

    travel_expenses_ws = SHEET.worksheet('TravelExpenses')
    travel_expenses_ws.append_row(trip_details)
    print(f"{trip_details} submitted to TravelExpenses worksheet")

def report_to_screen(worksheet_name):
    """
    This function will print worksheet details to screen
    """
    worksheet = SHEET.worksheet(worksheet_name)
    data = worksheet.get_all_records(worksheet)
    print(data)


print("\nWelcome to CCD Travel Expenses - 2023 Log & Approvals")

get_main_menu()

#trip_data_input = get_trip_data()
# All data entered is valid and verified, let expand it
print("adding this record")

#record = create_trip_record(trip_data_input)

#print(record)
#submit_trip_record(record)
#trip_name = expand_data(trip_data_input[0], 'En
# gineSize')
#trip_destination = expand_data(trip_data_input[1],'Distance')
# Create Trip record to be added to spreadsheet

