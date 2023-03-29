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


def view_expenses():
    # Read current month expenses from Google Sheets document
    # Check if expense is for current month
    current_month = datetime.today().month
    print(f'{"Date":<12}{"Amount":<10}{"Category":<15}')
    for row in expenses.get_all_values()[1:]:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        if expense_date.month == current_month:
            print(f"{row[2]:<12}${row[0]:<10}{row[1]:<15}")


def  edit_expense():
    # Read expense from Google Sheets document
    all_rows = expenses.get_all_values()[-10:][1:]

    # Display all expenses with their indexes
    print(f'{"Index":<6}{"Date":<12}{"Amount":<10}{"Category":<15}')
    for i, row in enumerate(all_rows):
        print(f"{i+1:<6}{row[2]:<12}${row[0]:<10}{row[1]:<15}")

    # Prompt user for index of the expense to edit
    index = int(input('Enter the index of the expense to edit: ')) -1

    # Check if index is valid
    if index < 0 or index >= len(all_rows):
        print('Invalid index')
        return
    
    # Prompt user for new expense details
    amount = input('Enter new expense amount: ')
    category = input('Enter new expense category (bills, food, pleasures): ')
    date = input('Enter new expense date (YYYY-MM-DD): ')

    # Check if date is valid
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print('Incorrect date format, should be YYYY-MM-DD')
        return

    # Update row in Google Sheets document
    row = [int(amount), category, date]
    expenses.update_cell(index + 2, 1, amount)
    expenses.update_cell(index + 2, 2, category)
    expenses.update_cell(index + 2, 3, date)
    print('Expense updated succesfully')