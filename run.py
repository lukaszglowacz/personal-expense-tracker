# Importing necessary libraries/modules
from datetime import datetime  # for working with dates and times
import gspread  # for interacting with Google Sheets API
from google.oauth2.service_account import Credentials  # for\
# authorizing access to Google Sheets API
import pyfiglet  # for printing ASCII art
import time  # for pausing the program execution for some time
import sys  # for interacting with the system
import os
import json

# Printing ASCII art banner
ascii_banner = pyfiglet.figlet_format("Personal\nExpense\nTracker")
print(ascii_banner)

# Define the required Google API scopes
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

# Load the credentials from the JSON file and authorize access
# to the required scopes
if "GOOGLE_CREDS_JSON" in os.environ:
    # ✅ Production / Heroku – creds from Config Var
    service_account_info = json.loads(os.environ["GOOGLE_CREDS_JSON"])
    CREDS = Credentials.from_service_account_info(service_account_info)
else:
    # ✅ Local development – fallback to creds.json file
    CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)

# Authorize access to the Google Sheets document
# using the authorized credentials
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('personal-expense-tracker')
EXPENSES = SHEET.worksheet('expenses')

# Define the expense categories
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


# Add expense function - add new expense and update it with Google
# Sheets document
def add_expense():
    # Display category options to the user
    print('')
    print(f'{"Index":<6}{"Category":<15}')
    for i, category in enumerate(CATEGORIES):
        print(f"{i+1:<6}{category:<15}")

    # Prompt user for category index
    while True:
        category_index_input = input(
            f"\nEnter the index of the new expense category"
            f" (1 - {len(CATEGORIES)}): "
        )
        if not category_index_input:
            continue
        try:
            category_index = int(category_index_input) - 1
            if category_index < 0 or category_index >= len(CATEGORIES):
                print(f"Invalid index. Please enter a number"
                      f" between 1 and {len(CATEGORIES)}")
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
            print("Incorrect date format. Please enter a valid"
                  " date in the format YYYY-MM-DD.")
            continue

    # Write expense to Google Sheets document
    row = [int(amount), CATEGORIES[category_index], str(date)]
    EXPENSES.append_row(row)
    print('\nExpense added successfully\n')

    # Ask user whether they want to add another
    # expense or return to the main menu
    go_back_add_expense()


# Edit expense function - edit expense and update
# it with Google Sheets document
def edit_expense():
    # Prompt user for year and month
    current_year = datetime.today().year
    while True:
        try:
            year = int(input(f'\nEnter year (1900 - {current_year}): '))
            if year < 1900 or year > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number'
                  f' between 1900 and {current_year} ')

    while True:
        max_month = 12 if year < current_year else datetime.today().month
        try:
            month = int(input(f'\nEnter month: (1 - {max_month}) '))
            if month < 1 or month > max_month:
                raise ValueError()
            # Check if there is any expense for the selected month
            chosen_date = datetime(year, month, 1)
            filtered_expenses = [
                expense for expense in EXPENSES.get_all_records()
                if (datetime.strptime(expense['Date'], '%Y-%m-%d').date()
                    .replace(day=1) == chosen_date.date())
            ]
            if len(filtered_expenses) == 0:
                print(f'There are no expenses for '
                      f'{chosen_date.strftime("%B %Y")}.'
                      f' Please select another year and month.')
                # Prompt user for another year
                while True:
                    try:
                        year = int(input(f'\nEnter year (1900 - '
                                         f'{current_year}): '))
                        if year < 1900 or year > current_year:
                            raise ValueError()
                        break
                    except ValueError:
                        print(f'Invalid year. Please enter a '
                              f'number between 1900 and {current_year} ')
                # Update max_month based on new year
                max_month = (
                    12 if year < current_year else datetime.today().month
                )
                continue
            # Display expenses in a table format
            print(f'{"Index":<10}{"Amount":<10}{"Category":<20}{"Date":<10}')
            for i, expense in enumerate(filtered_expenses):
                print(f'{i+1:<10}'
                      f'{expense["Amount"]:<10}'
                      f'{expense["Category"]:<20}'
                      f'{expense["Date"]:<10}')
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between '
                  f'1 and {max_month}. ')
            continue
    # Prompt user to choose an expense to edit
    while True:
        try:
            expense_index = int(input('\nEnter the index of '
                                      'expense to edit: '))
            if expense_index < 1 or expense_index > len(filtered_expenses):
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid index. Please enter '
                  f'a number between 1 and {len(filtered_expenses)}.')

    # Get the selected expense details
    selected_expense = filtered_expenses[expense_index-1]

    # Display the selected expense details
    print('\nSelected expense details:')
    print(f'Category: {selected_expense["Category"]}')
    print(f'Amount: {selected_expense["Amount"]}')
    print(f'Date: {selected_expense["Date"]}')

    # Prompt user to edit the expense details
    while True:
        try:
            edit_choice = input('\nWould you like to edit the category, '
                                'amount or date? (c / a / d) ')
            if edit_choice.lower() not in ['c', 'a', 'd']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter c '
                  '(category), a (amount) or d (date).')

    if edit_choice.lower() == 'c':
        # Display category options to the user
        print('')
        print(f'{"Index":<6}{"Category":<15}')
        for i, category in enumerate(CATEGORIES):
            print(f"{i+1:<6}{category:<15}")

        # Prompt user for new category index
        while True:
            category_index_input = input(
                f"\nEnter the index of the new expense category "
                f"(1 - {len(CATEGORIES)}): ")
            if not category_index_input:
                continue
            try:
                category_index = int(category_index_input) - 1
                if category_index < 0 or category_index >= len(CATEGORIES):
                    print(f"Invalid index. Please enter a number "
                          f"between 1 and {len(CATEGORIES)}")
                    continue
                break
            except ValueError:
                print('Invalid index. Please enter a valid number.')
                continue
        # Update the category for the selected expense
        selected_expense["Category"] = CATEGORIES[category_index]
        row_index = EXPENSES.find(selected_expense["Date"]).row
        EXPENSES.update_cell(row_index, 2, selected_expense["Category"])
        print('Category updated successfully')

        # Ask if user wants to edit more parameters
        while True:
            more_choice = input('\nDo you want to edit more '
                                'parameters for this expense? (y/n) ')
            if more_choice.lower() == 'y':
                # Prompt user to choose what to edit
                while True:
                    try:
                        edit_choice = input(
                            '\nWould you like to edit the '
                            'category, amount or date? (c / a / d) '
                        )
                        if edit_choice.lower() not in ['c', 'a', 'd']:
                            raise ValueError()
                        break
                    except ValueError:
                        print('Invalid choice. Please enter c '
                              '(category), a (amount) or d (date).')
                # Code for editing category, amount or date
                # Display the selected expense details
                print('\nSelected expense details:')
                print(f'Category: {selected_expense["Category"]}')
                print(f'Amount: {selected_expense["Amount"]}')
                print(f'Date: {selected_expense["Date"]}')

                if edit_choice.lower() == 'c':
                    # Display category options to the user
                    print('')
                    print(f'{"Index":<6}{"Category":<15}')
                    for i, category in enumerate(CATEGORIES):
                        print(f"{i+1:<6}{category:<15}")

                    # Prompt user for new category index
                    while True:
                        category_index_input = input(
                            f"\nEnter the index of the new expense "
                            f"category (1 - {len(CATEGORIES)}): "
                        )
                        if not category_index_input:
                            continue
                        try:
                            category_index = int(category_index_input) - 1
                            if category_index < 0 or category_index \
                                    >= len(CATEGORIES):
                                print(f"Invalid index. Please enter a number "
                                      f"between 1 and {len(CATEGORIES)}")
                                continue
                            break
                        except ValueError:
                            print('Invalid index. '
                                  'Please enter a valid number.')
                            continue
                    # Update the category for the selected expense
                    selected_expense["Category"] = CATEGORIES[category_index]
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(
                        row_index, 2, selected_expense["Category"]
                    )
                    print('Category updated successfully')

                elif edit_choice.lower() == 'a':
                    # Get new amount
                    while True:
                        amount_input = input('\nEnter new expense amount: ')
                        if not amount_input:
                            continue
                        try:
                            amount = round(float(amount_input))
                            if amount <= 0:
                                print('Invalid amount. '
                                      'Please enter a positive number.')
                                continue
                            break
                        except ValueError:
                            print('Invalid amount. '
                                  'Please enter a valid number.')
                            continue

                    # Update the amount for the selected expense
                    selected_expense["Amount"] = amount
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(
                        row_index, 1, selected_expense["Amount"]
                    )
                    print('Amount updated successfully')

                elif edit_choice.lower() == 'd':
                    # Get new date
                    while True:
                        date_input = input(
                            '\nEnter new expense date (YYYY-MM-DD): '
                        )
                        if not date_input:
                            continue
                        try:
                            date = datetime.strptime(
                                date_input, '%Y-%m-%d'
                            ).date()
                            if date > date.today():
                                print('Invalid date. '
                                      'Please enter a date '
                                      'in the past or today')
                                continue
                            break
                        except ValueError:
                            print("Incorrect date format. Please enter "
                                  "a valid date in the format YYYY-MM-DD.")
                            continue

                    # Update the date for the selected expense
                    # Get the row index for the selected expense
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    # Update the date for the selected expense
                    selected_expense["Date"] = str(date)
                    EXPENSES.update_cell(
                        row_index, 3, selected_expense["Date"]
                    )
                    print('Date updated successfully')

            elif more_choice.lower() == 'n':
                break
            else:
                print('Invalid choice. Please enter y (yes) or n (no).')

    elif edit_choice.lower() == 'a':
        # Get new amount
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

        # Update the amount for the selected expense
        selected_expense["Amount"] = amount
        row_index = EXPENSES.find(selected_expense["Date"]).row
        EXPENSES.update_cell(row_index, 1, selected_expense["Amount"])
        print('Amount updated successfully')

        # Ask if user wants to edit more parameters
        while True:
            more_choice = input(
                '\nDo you want to edit more parameters '
                'for this expense? (y/n) ')
            if more_choice.lower() == 'y':
                # Prompt user to choose what to edit
                while True:
                    try:
                        edit_choice = input(
                            '\nWould you like to edit the category, '
                            'amount or date? (c / a / d) ')
                        if edit_choice.lower() not in ['c', 'a', 'd']:
                            raise ValueError()
                        break
                    except ValueError:
                        print('Invalid choice. Please enter c '
                              '(category), a (amount) or d (date).')
                # Code for editing category, amount or date
                # Display the selected expense details
                print('\nSelected expense details:')
                print(f'Category: {selected_expense["Category"]}')
                print(f'Amount: {selected_expense["Amount"]}')
                print(f'Date: {selected_expense["Date"]}')

                if edit_choice.lower() == 'c':
                    # Display category options to the user
                    print('')
                    print(f'{"Index":<6}{"Category":<15}')
                    for i, category in enumerate(CATEGORIES):
                        print(f"{i+1:<6}{category:<15}")

                    # Prompt user for new category index
                    while True:
                        category_index_input = input(
                            f"\nEnter the index of the new expense category "
                            f"(1 - {len(CATEGORIES)}): "
                        )
                        if not category_index_input:
                            continue
                        try:
                            category_index = int(category_index_input) - 1
                            if category_index < 0 or category_index \
                                    >= len(CATEGORIES):
                                print(f"Invalid index. "
                                      f"Please enter a number between 1 "
                                      f"and {len(CATEGORIES)}")
                                continue
                            break
                        except ValueError:
                            print('Invalid index. '
                                  'Please enter a valid number.')
                            continue
                    # Update the category for the selected expense
                    selected_expense["Category"] = CATEGORIES[category_index]
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(
                        row_index, 2, selected_expense["Category"]
                    )
                    print('Category updated successfully')

                elif edit_choice.lower() == 'a':
                    # Get new amount
                    while True:
                        amount_input = input('\nEnter new expense amount: ')
                        if not amount_input:
                            continue
                        try:
                            amount = round(float(amount_input))
                            if amount <= 0:
                                print('Invalid amount. '
                                      'Please enter a positive number.')
                                continue
                            break
                        except ValueError:
                            print('Invalid amount. '
                                  'Please enter a valid number.')
                            continue

                    # Update the amount for the selected expense
                    selected_expense["Amount"] = amount
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(
                        row_index, 1, selected_expense["Amount"]
                    )
                    print('Amount updated successfully')

                elif edit_choice.lower() == 'd':
                    # Get new date
                    while True:
                        date_input = input(
                            '\nEnter new expense date (YYYY-MM-DD): '
                        )
                        if not date_input:
                            continue
                        try:
                            date = datetime.strptime(
                                date_input, '%Y-%m-%d'
                            ).date()
                            if date > date.today():
                                print('Invalid date. '
                                      'Please enter a date in the past '
                                      'or today')
                                continue
                            break
                        except ValueError:
                            print("Incorrect date format. "
                                  "Please enter a valid date in the "
                                  "format YYYY-MM-DD.")
                            continue

                    # Update the date for the selected expense
                    # Get the row index for the selected expense
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    # Update the date for the selected expense
                    selected_expense["Date"] = str(date)
                    EXPENSES.update_cell(
                        row_index, 3, selected_expense["Date"]
                    )
                    print('Date updated successfully')

            elif more_choice.lower() == 'n':
                break
            else:
                print('Invalid choice. Please enter y (yes) or n (no).')

    elif edit_choice.lower() == 'd':
        # Get new date
        while True:
            date_input = input('\nEnter new expense date (YYYY-MM-DD): ')
            if not date_input:
                continue
            try:
                date = datetime.strptime(date_input, '%Y-%m-%d').date()
                if date > date.today():
                    print('Invalid date. '
                          'Please enter a date in the past or today')
                    continue
                break
            except ValueError:
                print("Incorrect date format. "
                      "Please enter a valid date in the format YYYY-MM-DD.")
                continue

        # Update the date for the selected expense
        # Get the row index for the selected expense
        row_index = EXPENSES.find(selected_expense["Date"]).row
        # Update the date for the selected expense
        selected_expense["Date"] = str(date)
        EXPENSES.update_cell(row_index, 3, selected_expense["Date"])
        print('Date updated successfully')

        # Ask if user wants to edit more parameters
        while True:
            more_choice = input(
                '\nDo you want to edit more '
                'parameters for this expense? (y/n) '
            )
            if more_choice.lower() == 'y':
                # Prompt user to choose what to edit
                while True:
                    try:
                        edit_choice = input(
                            '\nWould you like to edit the '
                            'category, amount or date? (c / a / d) '
                        )
                        if edit_choice.lower() not in ['c', 'a', 'd']:
                            raise ValueError()
                        break
                    except ValueError:
                        print('Invalid choice. Please enter '
                              'c (category), a (amount) or d (date).')
                # Code for editing category, amount or date
                # Display the selected expense details
                print('\nSelected expense details:')
                print(f'Category: {selected_expense["Category"]}')
                print(f'Amount: {selected_expense["Amount"]}')
                print(f'Date: {selected_expense["Date"]}')

                if edit_choice.lower() == 'c':
                    # Display category options to the user
                    print('')
                    print(f'{"Index":<6}{"Category":<15}')
                    for i, category in enumerate(CATEGORIES):
                        print(f"{i+1:<6}{category:<15}")

                    # Prompt user for new category index
                    while True:
                        category_index_input = input(
                            f"\nEnter the index of the new expense "
                            f"category (1 - {len(CATEGORIES)}): "
                        )
                        if not category_index_input:
                            continue
                        try:
                            category_index = int(category_index_input) - 1
                            if category_index < 0 or category_index \
                                    >= len(CATEGORIES):
                                print(f"Invalid index. Please enter a number "
                                      f"between 1 and {len(CATEGORIES)}")
                                continue
                            break
                        except ValueError:
                            print('Invalid index. '
                                  'Please enter a valid number.')
                            continue
                    # Update the category for the selected expense
                    selected_expense["Category"] = CATEGORIES[category_index]
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(
                        row_index, 2, selected_expense["Category"]
                    )
                    print('Category updated successfully')

                elif edit_choice.lower() == 'a':
                    # Get new amount
                    while True:
                        amount_input = input('\nEnter new expense amount: ')
                        if not amount_input:
                            continue
                        try:
                            amount = round(float(amount_input))
                            if amount <= 0:
                                print('Invalid amount. '
                                      'Please enter a positive number.')
                                continue
                            break
                        except ValueError:
                            print('Invalid amount. '
                                  'Please enter a valid number.')
                            continue

                    # Update the amount for the selected expense
                    selected_expense["Amount"] = amount
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(
                        row_index, 1, selected_expense["Amount"]
                    )
                    print('Amount updated successfully')

                elif edit_choice.lower() == 'd':
                    # Get new date
                    while True:
                        date_input = input(
                            '\nEnter new expense date (YYYY-MM-DD): '
                        )
                        if not date_input:
                            continue
                        try:
                            date = datetime.strptime(
                                date_input, '%Y-%m-%d'
                            ).date()
                            if date > date.today():
                                print('Invalid date. Please enter '
                                      'a date in the past or today')
                                continue
                            break
                        except ValueError:
                            print("Incorrect date format. Please enter "
                                  "a valid date in the format YYYY-MM-DD.")
                            continue

                    # Update the date for the selected expense
                    # Get the row index for the selected expense
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    # Update the date for the selected expense
                    selected_expense["Date"] = str(date)
                    EXPENSES.update_cell(
                        row_index, 3, selected_expense["Date"]
                    )
                    print('Date updated successfully')

            elif more_choice.lower() == 'n':
                break
            else:
                print('Invalid choice. Please enter y (yes) or n (no).')

    # Ask user whether they want to edit
    # another expense or return to the main menu
    go_back_edit_expense()


# Year statement function - user can see how much
# expenses user have in entered year with category details
def year_statement():
    # Prompt user for year
    current_year = datetime.today().year
    while True:
        try:
            # Ask user to input the year to see the expenses for
            year = int(input(f'\nEnter year (1900 - {current_year}): '))
            # Validate user input - year should be
            # between 1900 and the current year
            if year < 1900 or year > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a '
                  f'number between 1900 and {current_year} ')

    # Read expenses form Google Sheets document
    # Retrieve all rows of expenses from the sheet, except the header row
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expenses for the chosen year
    total_expenses = {}

    # Iterate over all the rows in the sheet
    for row in all_rows:
        # Parse the date of the expense from the row
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')

        # Check if the expense was made in the chosen year
        if expense_date.year == year:
            # Get the category and amount of the expense from the row
            category = row[1]
            amount = int(row[0])

            # Add the amount to the total for the category
            if category in total_expenses:
                total_expenses[category] += amount
            else:
                total_expenses[category] = amount

    # Print total expenses for all categories
    # Calculate the total expenses for the chosen
    # year by summing up the expenses in all categories
    total_year_expense = sum(total_expenses.values())

    # Print the total expenses for all categories in the chosen year
    print(f"\nTotal expenses for all categories "
          f"in {year}: ${total_year_expense}\n")

    # Print the expenses for each category
    for category, amount in total_expenses.items():
        print(f"{category}: ${amount}")
        print('')

    # Ask user if they want to see statement for another year
    while True:
        try:
            choice = input(
                '\nDo you want to see another '
                'year statement? (y/n) '
            )
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        # If the user wants to see the expenses for
        # another year, call the function recursively
        year_statement()
    else:
        # Otherwise, return to the previous menu
        return

    # Ask user whether they want to see another year
    # statement or return to the main menu
    go_back_exp_year()


# Month statement function - user can see how much
# expenses user have in entered month with category details
def month_statement():
    # Prompt user for year and month
    current_year = datetime.today().year
    while True:
        try:
            # Ask user to input the year to see the expenses for
            year = int(input(f'\nEnter year (1900 - {current_year}): '))

            # Validate user input - year should be
            # between 1900 and the current year
            if year < 1900 or year > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a '
                  f'number between 1900 and {current_year} ')

    # Determine the maximum month to allow user
    # to choose, based on the year
    # If the year is less than the current year,
    # allow the user to choose any month
    # If the year is the current year,
    # allow the user to choose only up to the current month
    max_month = 12 if year < current_year else datetime.today().month
    while True:
        try:
            # Ask user to input the month to see the expenses for
            month = int(input(f'\nEnter month: (1 - {max_month}) '))

            # Validate user input - month should
            # be between 1 and the maximum allowed month
            if month < 1 or month > max_month:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a '
                  f'number between 1 and {max_month}. ')

    # Read expenses from Google Sheets document
    # Retrieve all rows of expenses from the sheet, except the header row
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expenses for all categories in the chosen month and year
    total_expenses = {}

    # Iterate over all the rows in the sheet
    for row in all_rows:
        # Parse the date of the expense from the row
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')

        # Check if the expense was made in the chosen month and year
        if expense_date.year == year and expense_date.month == month:
            # Get the category and amount of the expense from the row
            category = row[1]
            amount = int(row[0])

            # Add the amount to the total for the category
            if category in total_expenses:
                total_expenses[category] += amount
            else:
                total_expenses[category] = amount

    # Print total expenses for all categories
    # Calculate the total expenses for the chosen month
    # and year by summing up the expenses in all categories
    total_month_expense = sum(total_expenses.values())

    # Print the total expenses for all categories in the chosen month and year
    print(f"\nTotal expenses for all categories "
          f"in {month}/{year}: ${total_month_expense}\n")

    # Print the expenses for each category
    for category, amount in total_expenses.items():
        print(f"{category}: ${amount}")
        print('')

    # Ask user if they want to see statement for another year
    while True:
        try:
            choice = input('\nDo you want to see another statement? (y/n) ')

            # Validate user input - choice should be 'y' (yes) or 'n' (no)
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    # If the user chose 'y', call the corresponding function
    # to show the statement for another year or month
    if choice.lower() == 'y':
        month_statement()
    else:
        return

    # Ask user whether they want to see another month
    # statement or return to the main menu
    go_back_exp_month()


# Compare year expenses - user can compare two expenses
# year and get know in which year user spare more money
def compare_year_expenses():
    # Prompt user for two years
    current_year = datetime.today().year
    while True:
        try:
            # Ask the user to input the first year to compare expenses for
            year1 = int(input(
                f'\nEnter first year to compare '
                f'(1900 - {current_year}): '))

            # Validate user input - year should be
            # between 1900 and the current year
            if year1 < 1900 or year1 > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number '
                  f'between 1900 and {current_year} ')

    # Show user picked first year
    print(f'\nFirst year to compare: {year1}')

    while True:
        try:
            # Ask the user to input the second year to compare expenses for
            year2 = int(input(
                f'Enter second year to compare '
                f'(1900 - {current_year}): '))

            # Validate user input - year should be between 1900 and the
            # current year and should not be the same as the first year
            if year2 < 1900 or year2 > current_year:
                raise ValueError()
            if year2 == year1:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a different number '
                  f'between 1900 and {current_year}, excluding {year1}')

    # Show user picked first date
    print(f'\nSecond year to compare: {year2}')

    # Read expenses form Google Sheets document
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expenses for for each year and for each category
    expenses_by_year_category = {}
    total_expenses_by_year = {}

    # Iterate over all the rows in the sheet
    for row in all_rows:
        # Parse the date of the expense from the row
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        year = expense_date.year
        category = row[1]

        # Add the year to the expenses_by_year_category
        # and total_expenses_by_year dictionaries if it
        # doesn't already exist
        if year not in expenses_by_year_category:
            expenses_by_year_category[year] = {}
            total_expenses_by_year[year] = 0

        # Add the amount of the expense to the total
        # for the year and the category
        if category in expenses_by_year_category[year]:
            expenses_by_year_category[year][category] += int(row[0])
        else:
            expenses_by_year_category[year][category] = int(row[0])

        total_expenses_by_year[year] += int(row[0])

    # Compare expenses by category by category for the two years
    if year1 in expenses_by_year_category \
            and year2 in expenses_by_year_category:
        # Print the total expenses for each of the two years
        print(f"\nTotal expenses in {year1}: ${total_expenses_by_year[year1]}")
        print(f"Total expenses in {year2}: ${total_expenses_by_year[year2]}\n")

        # Calculate percentage difference between the two years
        diff = total_expenses_by_year[year1] - total_expenses_by_year[year2]
        percent = abs(diff / total_expenses_by_year[year1] * 100)

        # Print the percentage difference between the two years
        if diff > 0:
            print(f"{year1} is lower than {year2} by {percent:.2f}%\n")
        elif diff < 0:
            print(f"{year2} is lower than {year1} by {percent:.2f}%\n")
        else:
            print("Total expenses are the same in both years\n")

        # Print expenses in each category for each year
        print(f"\nExpenses by category in {year1}:")
        for category, amount in expenses_by_year_category[year1].items():
            print(f"{category}: ${amount}")

        print(f"\nExpenses by category in {year2}:")
        for category, amount in expenses_by_year_category[year2].items():
            print(f"{category}: ${amount}")

    else:
        print("\nOne or both of the years are not in the expenses data")

    # Ask user if they want to see statement for another year
    while True:
        try:
            choice = input(
                '\nDo you want to see another '
                'year statement? (y/n) '
            )
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    # Recurse if the user wants to see another year's statement,
    # else return to the main menu
    if choice.lower() == 'y':
        compare_year_expenses()
    else:
        return

    # Ask user whether they want to compare another
    # years or return to the main menu
    go_back_compare_year()


# Compare month expenses - user can compare two expenses
# month and get know in which month user spare more money
def compare_month_expenses():
    # Prompt user for year and month for the first date
    current_year = datetime.today().year
    while True:
        try:
            year1 = int(input(
                f'\nEnter year for first '
                f'date (1900 - {current_year}): '))
            if year1 < 1900 or year1 > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a '
                  f'number between 1900 and {current_year} ')

    while True:
        max_month = 12 if year1 < current_year else datetime.today().month
        try:
            month1 = int(input(
                f'\nEnter month for first '
                f'date (1 - {max_month}) '))
            if month1 < 1 or month1 > max_month:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a number '
                  f'between 1 and {max_month}. ')

    # Show user picked first date
    print(f'\nFirst date to compare: {year1}/{month1}')

    # Prompt user for year and month for the second date
    while True:
        try:
            year2 = int(
                input(f'\nEnter year for second date '
                      f'(1900 - {current_year}): ')
            )
            if year2 < 1900 or year2 > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a different '
                  f'number between 1900 and {current_year}, excluding {year1}')

    while True:
        max_month = 12 if year2 < current_year else datetime.today().month
        try:
            month2 = int(input(
                f'\nEnter month for second date (1 - {max_month}) '
            ))
            if month2 < 1 or month2 > max_month:
                raise ValueError()
            if year2 == year1 and month2 == month1:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between 1 '
                  f'and {max_month}, exclude {year1}/{month1} you picked '
                  f'in the first date. ')

    # Show user picked first date
    print(f'\nSecond date to compare: {year2}/{month2}')

    # Read expenses from Google Sheets document
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expense for both months
    expenses_by_month = {}
    for row in all_rows:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        year = expense_date.year
        month = expense_date.month
        if year == year1 and month == month1:
            category = row[1]
            amount = int(row[0])
            if category in expenses_by_month:
                expenses_by_month[category][0] += amount
            else:
                expenses_by_month[category] = [amount, 0]
        elif year == year2 and month == month2:
            category = row[1]
            amount = int(row[0])
            if category in expenses_by_month:
                expenses_by_month[category][1] += amount
            else:
                expenses_by_month[category] = [0, amount]

    # Print total expenses for both months
    total_month1_expenses = sum([expenses_by_month[category][0]
                                 for category in expenses_by_month])
    total_month2_expenses = sum([expenses_by_month[category][1]
                                 for category in expenses_by_month])

    print(f"\nTotal expenses for {year1}/{month1}: ${total_month1_expenses}\n")
    for category, amounts in expenses_by_month.items():
        print(f"{category}: ${amounts[0]}")

    print(f"\nTotal expenses for {year2}/{month2}: ${total_month2_expenses}\n")
    for category, amounts in expenses_by_month.items():
        print(f"{category}: ${amounts[1]}")

    # Calculate percentage difference between the two months
    if total_month1_expenses != 0:
        diff = total_month2_expenses - total_month1_expenses
        percent = abs(diff / total_month1_expenses * 100)
        if diff > 0:
            print(f"\nExpenses were lower in {year1}/{month1} "
                  f"by ${diff:} ({percent:.2f}%)")
        elif diff < 0:
            print(f"\nExpenses were lower in {year2}/{month2} "
                  f"by ${abs(diff):} ({percent:.2f}%)\n")
        else:
            print("\nExpenses were the same in both months")
    else:
        print("\nThere were no expenses in the first month.")

    # Ask user whether they want to compare another
    # months or return to the main menu
    go_back_compare_month()


# Function ask user if user want to go back to
# the menu or stays and add another expense
def go_back_add_expense():
    while True:
        try:
            choice = input('\nDo you want to go back to the main menu? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        main()
    else:
        add_expense()


# Function ask user if user want to go back to
# the menu or stays and edit another expense
def go_back_edit_expense():
    while True:
        try:
            choice = input('\nDo you want to go back to the main menu? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        main()
    else:
        edit_expense()


# Function ask user if user want to go back to the
# menu or stays and see another year statement
def go_back_exp_year():
    while True:
        try:
            choice = input('\nDo you want to go back to the main menu? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        main()
    else:
        year_statement()


# Function ask user if user want to go back to the
# menu or stays and see another month statement
def go_back_exp_month():
    while True:
        try:
            choice = input('\nDo you want to go back to the main menu? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        main()
    else:
        month_statement()


# Function ask user if user want to go back to
# the menu or stays and compare another years
def go_back_compare_year():
    while True:
        try:
            choice = input('\nDo you want to go back to the main menu? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        main()
    else:
        compare_year_expenses()


# Function ask user if user want to go back to the
# menu or stays and compare another months
def go_back_compare_month():
    while True:
        try:
            choice = input('\nDo you want to go back to the main menu? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        main()
    else:
        compare_month_expenses()


# Main called function, where other functions are called from main menu
def main():
    while True:
        print("Welcome to the Personal Expense Tracker!")
        print("\n===== MENU ======")
        print("\nPlease select an option:")
        print("1. Add an expense")
        print("2. Edit an expense")
        print("3. View expenses by year")
        print("4. View expenses by month")
        print("5. Compare expenses by year")
        print("6. Compare expenses by month")
        print("7. Quit")

        choice = input("\nEnter your choice (1-7): ")

        # Calls the appropriate function based on the user's choice
        if choice == '1':
            add_expense()
        elif choice == '2':
            edit_expense()
        elif choice == '3':
            year_statement()
        elif choice == '4':
            month_statement()
        elif choice == '5':
            compare_year_expenses()
        elif choice == '6':
            compare_month_expenses()
        elif choice == '7':
            print('\nGoodbye!')
            time.sleep(3)
            print('\nExiting program...')
            time.sleep(3)
            sys.exit()
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


# Main function which is only one function called when program starts
main()
