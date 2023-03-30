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

"""
The 3 worksheets in SHEET that are relevent to this app are
    TravelExpenses, Distance & EngineSize
Their FIELDS and sample data are outlined below and correct as of March 2023

TravelExpenses : Log of 2023 travel expenses/trip records
Fields & Example
STATUS	 SUBMITDATE	EMPLOYEE	  DESTINATION	AMOUNT	TRAVELDATE	ID-NUM
Approved 27 Mar 	Maura Murtagh Quarry	    17.36	Fri 20 Jan 	2023-21
Pending	 27 Mar 	Tarah Roche	  Quarry	    8.36	Sun 12 Feb  2023-23

NOTE : the ID_NUM field is auto generated when trip record added

Distance : Round trip distance from office location to destination
Fields & Example
DESTINATION	    DISTANCE-IN-KM
Browns	                55

EngineSize : Car engine size of employees authorised to claim travel expenses
EMPLOYEE	ENGINE-SIZE-cc	ALLOWANCE-PER-KM
Anne Tully	1600	        51.82

FYI
The allowances per KM are as follows
1200cc	41.80cent
1600cc	51.82cent
1400cc	43.40cent

"""


def get_main_menu():
    """
    This function is called from main()
    This function prints main menu to screen and calls prompt_user
    prompt_user returns the menu choice of the user
    the menu choice is returned to main()

    """

    main_menu = '''MAIN MENU
    1. Enter 1 to Log a trip for travel expenses
    2. Enter 2 to Generate a travel expenses report
    3. Enter 3 to Approve travel expenses
    4. Enter 4 to Exit
    '''
    print(main_menu)
    user_choice = prompt_user(4)
    return user_choice


def prompt_user(num):
    """
    This function prompts user to Enter a number from 1 to num
    where num is the size of the menu option being processed for instance
    main menu has 4 options so user will be asked to Enter 1,2,3 or 4
    whereas report menu has 3 options so user will be asked to Enter 1,2 or 3

    The user is prompted to enter a menu number within a while loop which will
    continue until a valid numeric is entered.  This will end the loop and the
    user menu number chosen is returned. Inside the while loop the user input
    is handled in a try block which caters for :
        blank input
        non-numeric value input
        numeric value input but out of range
    """
# controls while loop -breaks once valid user_choice from 1 to 'num' entered
    user_choice = 0
    # returns list of consecutive numbers 1 to num-1
    num_list = [i for i in range(1, num)]
    prompt = "Enter " + str(num_list).strip("[]") + " or " + str(num) + "\n"
    while user_choice not in range(1, num+1):
        try:
            u_input = input(prompt)
            # remove spaces if any input
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


def log_travel_expenses_trips():
    """
    This function is run when user chose option #1 from main menu, It is the
    main function for adding travel expense records to the database.

    The user is presented with information on the format & order of data to
    be input in order to add a travel expense record (trip) to the database &
    informed how the app works, then user is asked to enter their first record.

    Function  then enters a while loop which only breaks when user indicates
    they do not have any more trip records to enter.

    Once trip record data is input, it is validated by get_trip_data &
    not returned until correct information input (user informed all the while),
    Once return from get_trip_data we know we have correct data to construct a
    travel expenses record and create_trip_record is fired which returns a
    record, User is asked to verify this record is correct before submitting
    to the database, so record is either submitted or discarded depending
    User then asked if they have trip record to input and if not the while loop
    is broken & user returned to main menu - otherwise loop run again to
    enter another travel expense recorsd
    """
    print("\n CCD TRAVEL EXPENSE RECORDS 2023\n")

    valid_employees = return_nth_column("EngineSize", 1)
    valid_employees.pop(0)
    valid_destinations = return_nth_column("Distance", 1)
    valid_destinations.pop(0)
    print("You need Who Where & When to log the travel expense or trip"
          "\n\n Authorised Employees are :\n" +
          str(valid_employees).strip('[]').replace("'", "") +
          "\n Approved Destinations are   :\n" +
          str(valid_destinations).strip('[]').replace("'", "") +
          "\n\t Hints & Tips"
          "\n\t When inputting text you can use upper &/or lowercase,"
          "\n\t Enter firstname OR surname OR at least 3 letters from either."
          "\n\t Its the same with destination - just 3 letters will suffice."
          "\n\t This Smart App will expand substrings to the full format!"
          "\n\t Date of Travel to be in format dd/mm, Ex : 3/6 or 25/10."
          "\n\t Reimbursement Amount"
          "\n\t The App will calculate the amount due to employee based on "
          "\n\t distance travelled and car engine size, You do not need these"
          "\n\t figues as they already in the database (abeit a gsheet)"
          "\n\t Each trip record you submit to database will be automatically "
          "\n\t assigned a unique ID so go ahead now and enter the 3 items of"
          "\n\t trip information separated by commas in the following order :"
          "\n Employee Name, Destination, Date of Travel \n"
          )

    while True:
        trip_input = get_trip_data()
        # data input has been validated and verified at this stage
        record = create_trip_record(trip_input)
        headings = return_header_row("TravelExpenses")
        view_record = dict(zip(headings, record))
        print("This record has been created from the information you entered ")
        pprint(view_record, sort_dicts=False)
        print("Are you happy to submit this to the database?, Y or N please")
        answer = input()
        if "Y" in answer.upper():
            submit_trip_record(record)
        print("Do you have another trip to record? Y or N please ")
        answer = input()
        if "Y" not in answer.upper():
            break
        else:
            print("Enter Employee Name, Destination, Travel Date\n")
    return


def get_trip_data():
    """
    This function starts with a while loop that
    waits for user to enter 3 items to record the travel expense (trip)
    These items are NAME,DESTINATION, TRAVELDATE & only breaks out of the
    loop once the input is validated & 'Trip details accepted', therefore
    function only finishes on valid input from user & returns the data in
    list format having removed the comma delimiter
    The error exception handling is achieved in a 'try' block to check
    the input in a series of elif's & raise an error if
        input is blank
        input is too short (need 3 items entered aka 2 commas input)
        name or destination shorter than 3 letters

    Returns a list when valid trip record is input by user

    """
    while True:
        user_input = input()
        try:
            trip_input = user_input.split(",")
            if user_input == "":
                raise ValueError("Input is blank")
            elif len(trip_input) != 3:
                raise ValueError("3 items required")
            elif len(trip_input[0].strip()) < 3:
                raise ValueError("At least 3 letters from Employee required")
            elif len(trip_input[1].strip()) < 3:
                raise ValueError("At least 3 Destination letters required")
            elif validate_trip_data(trip_input):
                print("Trip details are accepted, Constructing the record...")
                break
        except ValueError as e:
            print(f"Invalid Input: {e} Please try again\n")
            print("Enter Employee Name, Destination, Travel Date")
    return trip_input


def validate_trip_data(trip_input):
    """
    This functions is used to validate the travel expense input by the user

    There are 3 items input, NAME, DESTINATION, TRAVELDATE
        NAME & Destination that are input can be substring > 2 letters
            NAME - needs to exist in the db (EngineSize ws gsheet)
            DESTINATION - needs to exist in the db (Distance ws gsheet)
        DATE - needs to be valid date
    This function does the following

    Divide the list of data into 3 string variables
    Verify the name, the destination, the date in series of nestd if's
    returning True if all If's passed
    or
    Returning False & Asking user to try again After appropriate message
    displayed to user as to what the problem with their input
    """
    # strip removes any leading/trailing whitespace
    name_input = trip_input[0].strip()
    destination_input = trip_input[1].strip()
    date_input = trip_input[2].strip()

    date_input_list = date_input.split("/")
    if verify_data(name_input, 'EngineSize'):
        if verify_data(destination_input, 'Distance'):
            if "/" in date_input and len(date_input) in range(3, 6):
                try:
                    date(
                        2023, int(date_input_list[1]), int(date_input_list[0])
                        )
                except ValueError as e:
                    print(f"{date_input} is Invalid : {e}, Try Again, Enter")
                    print("Employee Name, Destination, Travel Date\n")
                    return False
            else:
                print(f"Invalid date : {date_input}, Try Again, Enter")
                print("Employee Name, Destination, Travel Date\n")
                return False
        else:
            print(f"Invalid Destination : {destination_input}, Try Again")
            print("Enter Employee Name, Destination, Travel Date\n")
            return False
    else:
        print(f"Invalid Employee : {name_input}, Try Again, Enter")
        print("Employee Name, Destination, Travel Date\n")
        return False
    return True


def verify_data(data_input, worksheet):
    """
    This function check if data entered by user exists in DB/worksheet
    It is used to verify employee name and destination as both are in first
    column of corresponding worksheet
    """
    data_ws = SHEET.worksheet(worksheet)
    data_column = data_ws.col_values(1)
    # 1st column in EngineSize worksheet contains employee names
    # 1st column in Distance worksheet contains destinations
    if data_input.lower() in str(data_column).lower():
        return True
    else:
        return False


def create_trip_record(trip_input):
    """
    This function builds the Travel Expenses record (trip record)
    based on the data input by the user in the following steps

    1. The Employee Name and Destination details that were inut are
    converted/expanded to full text using expand_data function, This is
    required as user can input as little as 3 characters for name/destination

    2. Date input in dd/mm is converted to database format ie Tue 23 May
    There is no year saved in the date as database/gsheet is for 2023, There
    will be a new gsheet for every year

    3. Calculations are then carried out to determin the reimbursement amount
    due to employee, This is the only figure that the trip record holds, the
    distance and mileage rate (although km) applied are all done in the
    background
        Destination used to determine KM travelled in get_distance_in_km
        Employee Name (trip_name) used to determine Rate in rate_in_cent_per_km
    Both these figures used to calculate amount due to employee, Pleaae note
    that Civil service mileage rates depends on car engine size.

    All this information is used to construct the trip_record in List format
    & this value is returned, All new trip_records have STATUS = Pending

    """

    # expand substring to full name/destination strings
    trip_name = expand_data(trip_input[0].strip(), 'EngineSize')
    trip_destination = expand_data(trip_input[1].strip(), 'Distance')

    # convert dd/mm that was input into database/gsheet format
    date_input = trip_input[2].strip()
    date_input_list = date_input.split("/")
    trip_date = date(
        2023, (int((date_input_list[1]))), (int((date_input_list[0])))
        ).strftime('%a %d %b')

    # today is the submit date
    today = (date.today()).strftime('%d %b')
    # retrieve the mileage allowance for the named employee
    rate_in_cent_per_km = get_milage_rate(trip_name)
    # retrieve the distance for the trip
    distance = get_distance_in_km(trip_destination)
    # calculate in €'s the amount due to employee
    amount = round(((float(rate_in_cent_per_km) * int(distance))/100), 2)
    # Create the record that will be send to DB/TravelExpenses worksheet
    # Field names are STATUS SUBMITDATE EMPLOYEE DESTINATION AMOUNT TRAVELDATE
    trip_record = list((
        "Pending", today, trip_name[0], trip_destination[0], amount, trip_date
            ))
    return trip_record


def get_milage_rate(name):
    """
    This function returns the milage rate in cent per kilometer for the name
    sent in, the EngineSize worksheet has column headings for the employees
    that can claim travel NAME, ENGINE SIZE cc, Allowance per Km
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
    This function uses the destination send to it to find
    the assosiated distance and return this figure
    The informatio is held in a 2 column spreadsheet called Distance
    Column heading are Destination and Distance, The function identifies
    the row number of the destination value with the index() method
    the row_number is then used to get the corresponding distance
    and return that value
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
    & matches with an existing data in spreadsheet
    and returns the full item/longhand stored in spreadsheet
    """
    data_ws = SHEET.worksheet(worksheet)
    data_column = data_ws.col_values(1)

    full_data = [
        item for item in data_column if data_input.lower() in item.lower()
        ]
    # print(f"FYI : You entered {data_input} which when parsed is {full_data}")
    return full_data


def return_header_row(worksheet_name):
    """
    This function returns the values of the 1st row of the worksheet send in
    The headinga are used in displaying information to the user in various
    situations
    """
    the_ws = SHEET.worksheet(worksheet_name)
    headings = the_ws.row_values(1)
    return headings


def submit_trip_record(trip_details):
    """
    This function updates the TravelExpenses worksheet with trip record
    entered by the user, Confirmation is display to user
    """

    travel_expenses_ws = SHEET.worksheet('TravelExpenses')
    travel_expenses_ws.append_row(trip_details)
    print("Record submitted!, Reimbursement will apply once trip is approved")


def run_report_menu():
    """
    This function displays the report menu with 3 options
    User is them prompted to choose an option, all error/exception handling
    done in the prompt_user function, once report_menu_choice is validated
    the function takes appropriate action in a while lopo until
    user finally enters option #3 and is returned to main menu
    There are 2 reports options available for user to choose depending on
    the STATUS of the Travel Expense record - Pending or Approved
    """
    report_menu = """\nREPORT MENU
    1) Enter 1 to list PENDING  Travel Expense records
    2) Enter 2 to list APPROVED Travel Expense records
    3) Enter 3 to return to MAIN MENU
    """
    print(report_menu)
    report_menu_choice = prompt_user(3)

    while report_menu_choice != 3:
        if report_menu_choice == 2:
            print("\nList of Travel Expenses with Approved Status")
            run_approved_report()
        elif report_menu_choice == 1:
            print("\nList of Travel Expenses with Pending Status")
            run_pending_report()
        print(report_menu)
        report_menu_choice = prompt_user(3)
    return


def run_pending_report():
    """
    This function list all records in TravelExpense worksheet with
    Status=Pending
    """
    # STATUS is in 1st Column & is either Pending or Approved or Decline
    status_column = return_nth_column("TravelExpenses", 1)
    number_pending = status_column.count("Pending")
    if number_pending > 0:
        travel_expenses_ws = SHEET.worksheet("TravelExpenses")
        all_trips = travel_expenses_ws.get_values('A:G')
        pending_trip = [
            trip for trip in all_trips if trip[0] == "Pending"
            ]
        heading = return_header_row("TravelExpenses")
        # Column header in spreadsheet used for most report headings
        print(
            f"\n{heading[-1]}\t  {heading[1][0:6]}   {heading[2]}\t TO" +
            f"\t{heading[5][0:10]}   {heading[4]}"
            )
        for record in pending_trip:
            print(
                f"{record[-1]}\t  {record[1][0:10]}   {record[2]}" +
                f"\t{record[3]}\t{record[5][0:10]}   €{record[4]}"
                )
    # elif number_pending == 1:
        # printf("There is one record awaiting approval")
        print(
            f"\n SUMMARY : There are {number_pending} " +
            "records with Pending status"
            )
    else:
        pending_trip = []
        print(" NOTE There are no records waiting on approval at this time")
    return pending_trip


def run_approved_report():
    """
    This function list all records in TravelExpense worksheet with
    Status=Approved
    """
    # STATUS is in 1st Column & is either Pending or Approved
    status_column = return_nth_column("TravelExpenses", 1)
    number_approved = status_column.count("Approved")
    if number_approved > 0:
        travel_expenses_ws = SHEET.worksheet("TravelExpenses")
        all_trips = travel_expenses_ws.get_values('A:G')
        heading = return_header_row("TravelExpenses")
        # Column header in spreadsheet used for most report headings
        print(
            f"\n{heading[-1]}\t  {heading[1][0:6]}   {heading[2]}\t TO" +
            f"\t{heading[5][0:10]}   {heading[4]}"
        )
        approved_trip = [
            trip for trip in all_trips if trip[0] == "Approved"
            ]
        for record in approved_trip:
            print(
                f"{record[-1]}\t  {record[1][0:10]}   {record[2]}" +
                f"\t{record[3]}\t{record[5][0:10]}   €{record[4]}"
            )
        print(
            f"\n SUMMARY : There are {number_approved} records " +
            "with Approved Status"
            )
    else:
        print(
            " NOTICE : There are no records with Approved Status at this time"
            )
    return


def return_nth_column(worksheet_name, column_number):
    """
    This function will return all values in #column_number of worksheet_name
    """
    worksheet = SHEET.worksheet(worksheet_name)
    data = worksheet.col_values(column_number)
    return data


def approve_pending_records():
    """
    This function is fired when user picks option #3 from the main menu
    This function display all pending travel expense records to the screen
    and gives user the choice of approving all together or one by one
    Records are approved by changing the STATUS from Pending to Approved
    using update_cell, The record is identified by the uniqueID automatically
    assigned to column G on TravelExpenses worksheet (aka the database)
    (NUM-ID generated by if(A?<>"",CONCATENATE("2023-",row()),""))

    This function could be improve by creating sub function to carry out the
    the 2 while loops here to 'update_cell' & calling from here
    """

    pending_records = run_pending_report()
    number_pending = len(pending_records)
    if number_pending > 0:
        print("Do you want to approve all records at once?, Enter Y or N")
        answer = input()
        if "Y" in answer.upper():
            i = 0
            travel_expenses_ws = SHEET.worksheet("TravelExpenses")
            while i < number_pending:
                row_number = pending_records[i][-1]
                travel_expenses_ws.update_cell(
                    int(row_number[5:]), 1,  "Approved"
                        )
                i += 1
            print(f"{number_pending} records approved")
        else:
            i = 0
            travel_expenses_ws = SHEET.worksheet("TravelExpenses")
            while i < number_pending:
                print("Do you approve? Y or N")
                print(pending_records[i])
                answer = input()
# ID # is prepended with 2023-##, ID is in last column or [-1] on a Python list
                row_number = pending_records[i][-1]
                if "Y" in answer.upper():
                    travel_expenses_ws.update_cell(
                        # slice '2023-' from row_number
                        int(row_number[5:]), 1,  "Approved"
                        )
                    print("Approved...next record")
                else:
                    print("Not approved...next record")
                i += 1
    else:
        print("Nothimg to do here!!")


def main():
    """
    Main program loop
    Print the main menu which gives user 4 options with number 4 being to exit
    Act on the other 3 options by firing the follwoing functions
    #1 - Add travel expense record to the database - log_travel_expenses_trips
    #2 - Reports section - a sub-menu for user to choose which report to run
    #3 - Approval section - this is where a manager would approve or not
        each travel expense record before reimbursement can be made
    Once work is complete on each option, the main menu continually displayed
    until the user enters option 4 to exit the app
    """

    user_main_choice = get_main_menu()
    # get choice back its type int 1 to 4
    while user_main_choice != 4:
        if user_main_choice == 3:
            approve_pending_records()
            print("End of Approve work this time")
        elif user_main_choice == 2:
            run_report_menu()
        elif user_main_choice == 1:
            log_travel_expenses_trips()
        user_main_choice = get_main_menu()
    print(" Goodbye")


print("\nWelcome to CCD Travel Expenses - 2023 Log & Approvals")
main()
