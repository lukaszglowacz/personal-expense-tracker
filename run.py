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
    print('Select a expense category: \n')
    for i, category in enumerate(CATEGORIES):
        print(f"{i+1}. {category}")

    # Prompt user for category index
    
    while True:
        index_input = input('\nEnter the index of the expense category: ')
        if not index_input:
            continue
        try:
            index = int(index_input) - 1
            if index < 0 or index >= len(CATEGORIES):
                print(f"Invalid index. Please enter a number between 1 and {len(CATEGORIES)}")
                continue
            break
        except ValueError:
            print('Invalid index. Please enter a valid number.')
            continue

    # Get expense details
    # Get amount only with numbers and change it to integers
    while True:  
        amount_input = input('Enter expense amount: ')
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
        date_input = input('Enter expense date (YYYY-MM-DD): ')
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
    row = [amount, CATEGORIES[index], date.strftime('%Y-%m-%d')]
    EXPENSES.append_row(row)
    print('Expense added successfully')

add_expense()

def view_expenses():
    # Read current month expenses from Google Sheets document
    # Check if expense is for current month
    current_month = datetime.today().month
    print(f'{"Date":<12}{"Amount":<10}{"Category":<15}')
    for row in EXPENSES.get_all_values()[1:]:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        if expense_date.month == current_month:
            print(f"{row[2]:<12}${row[0]:<10}{row[1]:<15}")



def  edit_expense():
    # Read expense from Google Sheets document
    all_rows = EXPENSES.get_all_values()[-10:][1:]

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
    EXPENSES.update_cell(index + 2, 1, amount)
    EXPENSES.update_cell(index + 2, 2, category)
    EXPENSES.update_cell(index + 2, 3, date)
    print('Expense updated succesfully')



def detail_expense():
    # Read expenses from Google Sheets document
    all_rows = EXPENSES.get_all_values()[1:]

    # Print expense details for the current month
    current_month = datetime.today().month
    total_expenses = 0
    for row in all_rows:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        if expense_date.month == current_month:
            total_expenses += int(row[0])
    print(f"Total expenses for the current month: ${total_expenses}")

    # Define expense categories
    categories = [
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

    # Display category options to the user
    print('\nSelect a category to view detailed expenses:')
    for i, category in enumerate(categories):
        print(f"{i+1}. {category}")

    #Prompt user for category index
    index = int(input('Enter the index of the expense category: ')) -1

    # Check if index is valid
    if index < 0 or index >= len(categories):
        print('Invalid index')
        return

    # Calculate and print total expenses for selected category
    category = categories[index]
    category_total = 0
    for row in all_rows:
        if row[1] == category:
            category_total += int(row[0])
            print(f"\nTotal expenses for {category}: ${category_total}")


