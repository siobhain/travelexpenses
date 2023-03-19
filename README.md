
# CCD Travel Expenses Console App

Python Console app that automates logging and approval of CCD travel expenses using api to a gspread sheet.  CCD is a ficticious SME.

 pip3 install gspread google-auth dependencies that had to be installed

## Introduction
mileage rates
reimbursement to employee for work travel
payment can be made tax free by the amoutn of business km travelled, journeys to/from home cannot be clainmed as mileage.
There is a maximum mileage allowance per kilometre that the employer can reimburse tax-free. The mileage allowance rates depend on the type of vehicle. These maximum amounts are based on the Civil Service rates and can be found on the website of the Irish Revenue. Cars Motor travel rates 

CCD is a fictional SME which repay 4 employees when they use their private car for business purposes. They follow the Civil Service rates from www.revenue.ie. 
This payment can be made, tax free, by the amount of business kilometres travelled. You can either:

![Inital Flowchart](docs/flowchart.PNG)

## Goal
## Features
existing & future
## Data Model
A google sheet was used to store the trips. The sheet consists of 3 worksheets, "Employee", "Distance" & "Trip".  Employee and Distance are static worksheet that give python infor needed to calculate amount due for each trip.  Trip is dynamic worksheet updated via the colsol in 2 seperate processes.  First trip destails entered via console. 2nd Trip approved by manager so reimbursment can be made.

## Testing
manually tested by doing th following

passed code through PEP8 linter & confirmed no problems
Given invalid inputs : ie string when number expected, same trip twice
tested in local console and in CI Heroku terminal

## Bugs

TypeError: Object of type datetime is not JSON serializable




### Validator TEsting
PEP8 - no errors returned from pep8online.com

## Deployment
The project was deployed using Code I mock terminal for Heroku

Steps
fork or clone this repo
creat a new Heroku app
set the buildbacks to Python and NodeJS in that order
Link rhe Heroku app to the repo
click on deploy

## TEchnology used

gspread - allows communication with google sheets
colorama -??? TBD
google.oauth2.service_account : Credentials : used to validate and grant access to google service accounts
lucid - flow charts

## Credits
CI for the mock terminal



## Reminders

* Your code must be placed in the `run.py` file
* Your dependencies must be placed in the `requirements.txt` file
* Do not edit any of the other files or your code may not deploy properly

## Creating the Heroku app

When you create the app, you will need to add two buildpacks from the _Settings_ tab. The ordering is as follows:

1. `heroku/python`
2. `heroku/nodejs`

You must then create a _Config Var_ called `PORT`. Set this to `8000`

If you have credentials, such as in the Love Sandwiches project, you must create another _Config Var_ called `CREDS` and paste the JSON into the value field.

Connect your GitHub repository and deploy as normal.

## Constraints

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

-----
Happy coding!