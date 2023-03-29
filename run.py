from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Define the credentials
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)

# Authorize access to Google Sheets document
SHEET = GSPREAD_CLIENT.open('personal-expense-tracker')
expenses = SHEET.worksheet('expenses')


def add_expense():
    # Get expense details
    amount = input('Enter expense amount: ')
    category = input('Enter expense category (bills, food, pleasures: ')
    date = input('Enter expense date (YYYY-MM-DD): ')

    # Check if date is valid
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print("Incorrect date format, shoul be YYYY-MM-DD")
        return

    # Write expense to Google Sheets document
    row = [int(amount), category, date]
    expenses.append_row(row)
    print('Expense added succesfully')