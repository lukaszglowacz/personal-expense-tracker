from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pyfiglet

ascii_banner = pyfiglet.figlet_format("Personal\nExpense\nTracker")
print(ascii_banner)

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
EXPENSES = SHEET.worksheet('expenses')
# Define expense categories
CATEGORIES = [
    'Housing',
    'Transportation',
    'Food',
    'Utilities',
    'Clothing',
    'Healthcare',
    'Insurance',
    'Supplies',
    'Personal',
    'Debt',
    'Retirement',
    'Education',
    'Savings',
    'Gifts',
    'Entertainment'
]

def add_expense():
    # Display category options to the user
    print('')
    print(f'{"Index":<6}{"Category":<15}')
    for i, category in enumerate(CATEGORIES):
        print(f"{i+1:<6}{category:<15}")
    
    # Prompt user for category index
    while True:
        category_index_input = input(f"\nEnter the index of the new expense category (1 - {len(CATEGORIES)}): ")
        if not category_index_input:
            continue
        try:
            category_index = int(category_index_input) - 1
            if category_index < 0 or category_index >= len(CATEGORIES):
                print(f"Invalid index. Please enter a number between 1 and {len(CATEGORIES)}")
                continue
            break
        except ValueError:
            print('Invalid index. Please enter a valid number.')
            continue

    # Get expense details
    # Get amount only with numbers and change it to integers
    while True:  
        amount_input = input('\nEnter expense amount: ')
        if not amount_input:
            continue
        try:
            amount = round(float(amount_input))
            if amount <= 0:
                print('Invalid amount. Please enter a positive number.')
                continue
            break
        except ValueError:
            print('Invalid amount. Please enter a valid number.')
            continue

    # Get expense date
    while True:
        date_input = input('\nEnter expense date (YYYY-MM-DD): ')
        if not date_input:
            continue
        try:
            date = datetime.strptime(date_input, '%Y-%m-%d').date()
            if date > date.today():
                print('Invalid date. Please enter a date in the past or today')
                continue
            break
        except ValueError:
            print("Incorrect date format. Please enter a valid date in the format YYYY-MM-DD.")
            continue

    # Write expense to Google Sheets document
    row = [int(amount), category, str(date)]
    EXPENSES.append_row(row)
    print('\nExpense added successfully\n')



def  edit_expense():
    # Read expense from Google Sheets document
    all_rows = EXPENSES.get_all_values()[-10:][1:]

    # Display all expenses with their indexes
    print(f'{"Index":<6}{"Date":<12}{"Amount":<10}{"Category":<15}')
    for i, row in enumerate(all_rows):
        print(f"{i+1:<6}{row[2]:<12}${row[0]:<10}{row[1]:<15}")

    # Prompt user for index of the expense to edit
    valid_indexes = [str(i+1) for i in range(len(all_rows))]
    last_valid_index = valid_indexes[-1]
    index = None
    while index is None:
        index_input = input(f'\nEnter the index of the expense to edit (1 - {last_valid_index}): ')
        if index_input not in valid_indexes:
            print(f'Invalid index. Please enter a number between 1 and {len(all_rows)}. ')
            continue
        index = int(index_input) - 1

    
    # Display category options to the user
    print('')
    print(f'{"Index":<6}{"Category":<15}')
    for i, category in enumerate(CATEGORIES):
        print(f"{i+1:<6}{category:<15}")

    # Prompt user for category index
    while True:
        category_index_input = input(f"\nEnter the index of the new expense category (1 - {len(CATEGORIES)}): ")
        if not category_index_input:
            continue
        try:
            category_index = int(category_index_input) - 1
            if category_index < 0 or category_index >= len(CATEGORIES):
                print(f"Invalid index. Please enter a number between 1 and {len(CATEGORIES)}")
                continue
            break
        except ValueError:
            print('Invalid index. Please enter a valid number.\n')
            continue

    # Get expense details
    # Get amount only with numbers and change it to integers
    while True:  
        amount_input = input('\nEnter new expense amount: ')
        if not amount_input:
            continue
        try:
            amount = round(float(amount_input))
            if amount <= 0:
                print('Invalid amount. Please enter a positive number.')
                continue
            break
        except ValueError:
            print('Invalid amount. Please enter a valid number.')
            continue
    
        # Get expense date
    while True:
        date_input = input('\nEnter new expense date (YYYY-MM-DD): ')
        if not date_input:
            continue
        try:
            date = datetime.strptime(date_input, '%Y-%m-%d').date()
            if date > date.today():
                print('Invalid date. Please enter a date in the past or today')
                continue
            break
        except ValueError:
            print("Incorrect date format. Please enter a valid date in the format YYYY-MM-DD.")
            continue


    # Update row in Google Sheets document
    row = [int(amount), category, str(date)]
    EXPENSES.update_cell(index + 2, 1, amount)
    EXPENSES.update_cell(index + 2, 2, category)
    EXPENSES.update_cell(index + 2, 3, str(date))
    print('\nExpense updated succesfully\n')


def detail_expense():
    # Prompt user for year and month
    current_year = datetime.today().year
    while True:
        try:
            year = int(input('\nEnter year: '))
            if year < 1900 or year > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number between 1900 and {current_year} ')
    
    max_month = 12 if year < current_year else datetime.today().month
    while True:
        try:
            month = int(input(f'\nEnter month (1 - {max_month}) '))
            if month < 1 or month > max_month:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between 1 and {max_month}. ')

            

detail_expense()


def view_expenses():
    # Read current month expenses from Google Sheets document
    # Check if expense is for current month
    current_month = datetime.today().month
    print(f'{"Date":<12}{"Amount":<10}{"Category":<15}')
    for row in EXPENSES.get_all_values()[1:]:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        if expense_date.month == current_month:
            print(f"{row[2]:<12}${row[0]:<10}{row[1]:<15}")