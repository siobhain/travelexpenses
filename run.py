"""
    CCD Travel Expenses Console App
"""
from datetime import date
from pprint import pprint
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
    This function asks user to enter a number from 1 to 4
    The input string is checked for validation in a 'try'
    The user will be asked to try again until a valid number is entered

    """

    main_menu = '''MAIN MENU
        1) Enter 1 to Log a trip for travel expenses
        2) Enter 2 to Generate a travel expenses report
        3. Enter 3 to Approve travel expenses
        4. Enter 4 to Exit
        '''
    print(main_menu)
    user_choice = prompt_user(4)
    return user_choice


def prompt_user(num):
    """
    This function
    process users input from 1 to num

    removes spaces from input
    check for number between 1 nad num passed into the function
    caters for all occurances of invalid input from nothing inout

    """
    user_choice = 0
    # returns list of consecutive numbers 1 to num-1
    num_list = [i for i in range(1, num)]
    prompt = "Enter " + str(num_list).strip("[]") + " or " + str(num) + "\n"
    while user_choice not in range(1, num+1):
        try:
            u_input = input(prompt)
            # remove spaces if any
            user_input = u_input.replace(" ", "")
            if user_input == "":
                raise ValueError(" Input is blank")
            elif not user_input.isnumeric():
                raise ValueError(" Numeric value only")
            elif int(user_input) in range(1, num+1):
                user_choice = int(user_input)
            else:
                raise ValueError(" Numeric out of range")
        except ValueError as e:
            print(f" {e}, Please try again. \n")
    return int(user_choice)

def log_a_trip():  #  change this name
    """
    Asks user to log a trip
    """
    print("\n CCD TRAVEL EXPENSE RECORDS 2023\n")

    valid_employees = return_nth_column("EngineSize",1)
    valid_employees.pop(0)
    valid_destinations = return_nth_column("Distance", 1)
    valid_destinations.pop(0)
  
    print("Here you will need Employee Name, Destination & Date of travel" +
          "to record the trip"
          "\n\n Authorised Employees are : " + 
          str(valid_employees).strip('[]').replace("'","") +
          "\n Valid Destinations are : " + 
          str(valid_destinations).strip('[]').replace("'","") +
          "\n Date of Travel should be in format dd/mm, Example : 3/6 or 10/12"
          "\nNOTES\n You do not need to enter the full name or destination, "+
          "A substring of at least 3 letters of either will suffice"
          "\n The App will expand the substring to its full format & " +
          "It is NOT case sensitive so you can use upper or lowercase"
          "\n\t Now enter the trip information separated by commas to log a trip"
          "\n\t\t Employee Name, Destination, Travel Date in dd/mm format\n"
          )

    while True:
        trip_input = get_trip_data()  
        # data has been validated and verified at this stage
        record = create_trip_record(trip_input)
        print("This record has been created from the informaiton you entered ")
        print(record)
        print("Are you sure you want to submit this record?, Y or N please")
        answer = input()
        if "Y" in answer.upper():
            submit_trip_record(record)
        print("Do you have another trip to record? Y or N please ")
        answer = input()
        if "Y" not in answer.upper():
            break
    print("Back to MAIN MENU")    

    
def get_trip_data():
    """
    Ask user to enter 3 items to record the trip
    """
    while True:
        user_input = input()
        try:
            trip_input = user_input.split(",")
            if user_input == "":
                raise ValueError("Input is blank")
            elif len(trip_input) != 3:
                raise ValueError(f"3 items required")
            elif len(trip_input[0].strip()) < 3:
                raise ValueError(f"At least 3 letters from Employee required")
            elif len(trip_input[1].strip()) < 3:
                raise ValueError(f"At least 3 letters from Destination required")
            elif validate_trip_data(trip_input):
                print("Trip details accepted, Logging it")
                break
            # else:
            #     print(
            #         "Invalid Input Try Again \n ENTER  " +
            #         "Employee Name, Destination, dd/mm"
            #         ) 
        except ValueError as e:
                print(f"Invalid Input: {e} Please try again\n")
                print(
                    "    Enter Employee Name, Destination, " +
                    "Travel Date in dd/mm format\n" 
                    )
                
    return trip_input


def validate_trip_data(trip_input):
    """
    Three items input for trip
    NAME - needs to match name in spreadsheet
    DESTINATION - needs to match destination in spreadsheet
    DATE - needs to be valid date

    """
    name_input = trip_input[0].strip()
    destination_input = trip_input[1].strip()
    date_input = trip_input[2].strip()
    date_input_list = date_input.split("/")
    if verify_data(name_input, 'EngineSize'):
        if verify_data(destination_input, 'Distance'):
            if "/" in date_input and len(date_input) in range(3,6):
                try:
                    trip_date = date(
                        2023, int(date_input_list[1]), int(date_input_list[0])
                        )
                    print(trip_date)
                except ValueError as e:
                    print(f"{date_input} is Invalid : {e}, Try Again")
                    return False
            else:       
                print(f"Invalid date : {date_input}, Try Again")
                return False 
        else:
            print(f"Invalid Destination : {destination_input}, Try Again")
            return False
    else:
        print(f"Invalid Name : {name_input} " +
              "\n\tUse at least 3 letters from an item in the authorised list " +
              " Try Again")
        return False
    return True


def verify_data(data_input, worksheet):
    """
    This function check if data is in worksheet, used for employee name
    and destination aa both in first column of worksheet
    """
    data_worksheet = SHEET.worksheet(worksheet)
    data_column = data_worksheet.col_values(1)
    # 1st column in EngineSize worksheet contains employee names
    # 1st column in Distance worksheet contains destinations

    if data_input.lower() in str(data_column).lower():
        return True
    else:
        return False


def create_trip_record(trip_input):
    """
    Expand the data/
    perform processing before entry to spreadsheet
    record needs to be in following order
    STATUS SUBMITDATE NAME DESTINATION AMOUNT TRAVELDATE
    """
    # get full name and destination strings
    trip_name = expand_data(trip_input[0].strip(), 'EngineSize')
    trip_destination = expand_data(trip_input[1].strip(), 'Distance')

    # convert dd/mm that was input to the gsheet date format
    date_input_list = (trip_input[2].strip()
    ).split("/")
    trip_date = date(
        2023, (int((date_input_list[1]))), (int((date_input_list[0])))
        ).strftime('%a %d %b %Y')

    # today is the submit date
    today = (date.today()).strftime('%a %d %b %Y')

    # retrieve the milage allowance for the employee
    rate_in_cent_per_km = get_milage_rate(trip_name)
    # retrieve the distance for the trip
    distance = get_distance_in_km(trip_destination)
    # calculate in €'s the amount due to employee
    amount = round(((float(rate_in_cent_per_km) * int(distance))/100), 2)
    # Create the record that will be send to TravelExpenses worksheet
    trip_record = list((
        "PENDING", today, trip_name[0], trip_destination[0], amount, trip_date
            ))
    #pprint(trip_record)
    return trip_record


def get_milage_rate(name):
    """
    This function returns the milage rate in cent per kilometer for the name
    sent in the EngineSize worksheet has column headings for the employees that
    can claim travel NAME, ENGINE SIZE cc,Allowance per Km
    There is a row for each employee that can claim travel expanses
    Open woksheet, find index of employee to get rate for that employee
    """
    enginesize_ws = SHEET.worksheet('EngineSize')
    employees_column = enginesize_ws.col_values(1)
    rate_column = enginesize_ws.col_values(3)
    name_string = name[0]
    row_number = employees_column.index(name_string)

    return rate_column[row_number]


def get_distance_in_km(destination):
    """
    This function uses the destination send to it to #
    find the distance of said destination from spreadsheet
    """
    distance_ws = SHEET.worksheet('Distance')
    destination_column = distance_ws.col_values(1)
    distance_column = distance_ws.col_values(2)
    destination_string = destination[0]
    row_number = destination_column.index(destination_string)
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


def run_report_menu():
    """
    This function asked user what report they want to see

    """
    report_menu = """REPORT MENU
    1) Enter 1 to list PENDING  Travel Expense records
    2) Enter 2 to list APPROVED Travel Expense records
    3) Enter 3 to return to MAIN MENU OR EXIT
    """
    print(report_menu)

    report_menu_choice = prompt_user(3)

    print("You chose report menu number " + int(report_menu_choice))
    # run_pending_report()


def run_pending_report():
    """
    This function list all records in TravelExpense worksheet with
    Status=PENDING
    """
    # STATUS is in 1st Column & is either PENDING or APPROVED or DECLINE
    status_column = return_nth_column("TravelExpenses", 1)
    number_pending = status_column.count("PENDING")
    if number_pending > 0:
        print(f" There are {number_pending} awaiting approval")
        travel_expenses_ws = SHEET.worksheet("TravelExpenses")
        all_trips = travel_expenses_ws.get_values('A:F')
        pending_trip = [
            trip for trip in all_trips if trip[0] == "PENDING"
            ]
        for record in pending_trip:
            print(
                f"\t{record[2]}\t{record[3]}\t{record[5][0:10]}   €{record[4]}"
                )
    else:
        print(" There are none awaiting approval")


def run_approved_report():
    """
    This function list all records in TravelExpense worksheet with
    Status=PENDING
    """
    # STATUS is in 1st Column & is either PENDING or APPROVED or DECLINE
    status_column = return_nth_column("TravelExpenses", 1)
    number_pending = status_column.count("APPROVED")
    if number_pending > 0:
        print(f" There are {number_pending} APPROVED")
        travel_expenses_ws = SHEET.worksheet("TravelExpenses")
        all_trips = travel_expenses_ws.get_values('A:F')
        pending_trip = [
            trip for trip in all_trips if trip[0] == "APPROVED"
            ]
        for record in pending_trip:
            print(
                f"\t{record[2]}\t{record[3]}\t{record[5][0:10]}   €{record[4]}"
                )
    else:
        print(" There are no approved records")


def return_nth_column(worksheet_name, column_number):
    """
    This function will return all values in #column_number of worksheet_name
    """
    worksheet = SHEET.worksheet(worksheet_name)
    data = worksheet.col_values(column_number)
    return data

def main():
    """ Main program loop
    """

    user_main_choice = get_main_menu()
    # get choice back its type int 1 to 4
    while user_main_choice != 4:
        if user_main_choice == 3:
            print("Manager Approvals")   
        elif  user_main_choice == 2:
            print("Run Report menu")
        elif user_main_choice == 1:
            print("Log a trip")
            log_a_trip()
        user_main_choice = get_main_menu()
    
    print(" Goodbye")


    

print("\nWelcome to CCD Travel Expenses - 2023 Log & Approvals")
main()

# user_main_choice = get_main_menu()  # PROBLEM saying user main is a constant
# print("You picked" + str(user_main_choice))

# run_report_menu()

# trip_data_input = get_trip_data()
# All data entered is valid and verified, let expand it
# print("get trip returned"+str(trip_data_input))

# record = create_trip_record(trip_data_input)

# print(record)
# submit_trip_record(record)
# trip_name = expand_data(trip_data_input[0], 'En
# gineSize')
# trip_destination = expand_data(trip_data_input[1],'Distance')
# Create Trip record to be added to spreadsheet
