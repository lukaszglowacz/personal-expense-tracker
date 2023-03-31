from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pyfiglet
import time
import sys

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
    row = [int(amount), CATEGORIES[category_index], str(date)]
    EXPENSES.append_row(row)
    print('\nExpense added successfully\n')

    go_back_add_expense()

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
            print(f'Invalid year. Please enter a number between 1900 and {current_year} ')
    
    while True:
        max_month = 12 if year < current_year else datetime.today().month
        try:
            month = int(input(f'\nEnter month: (1 - {max_month}) '))
            if month < 1 or month > max_month:
                raise ValueError()
            # Check if there is any expense for the selected month
            chosen_date = datetime(year, month, 1)
            filtered_expenses = [expense for expense in EXPENSES.get_all_records() if datetime.strptime(expense['Date'], '%Y-%m-%d').date().replace(day=1) == chosen_date.date()]
            if len(filtered_expenses) == 0:
                print(f'There are no expenses for {chosen_date.strftime("%B %Y")}. Please select another year and month.')
                # Prompt user for another year
                while True:
                    try:
                        year = int(input(f'\nEnter year (1900 - {current_year}): '))
                        if year < 1900 or year > current_year:
                            raise ValueError()
                        break
                    except ValueError:
                        print(f'Invalid year. Please enter a number between 1900 and {current_year} ')
                # Update max_month based on new year
                max_month = 12 if year < current_year else datetime.today().month
                continue
            # Display expenses in a table format
            print(f'{"Index":<10}{"Amount":<10}{"Category":<20}{"Date":<10}')
            for i, expense in enumerate(filtered_expenses):
                print(f'{i+1:<10}{expense["Amount"]:<10}{expense["Category"]:<20}{expense["Date"]:<10}')
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between 1 and {max_month}. ')
            continue
    # Prompt user to choose an expense to edit
    while True:
        try:
            expense_index = int(input('\nEnter the index of expense to edit: '))
            if expense_index < 1 or expense_index > len(filtered_expenses):
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid index. Please enter a number between 1 and {len(filtered_expenses)}.')

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
            edit_choice = input('\nWould you like to edit the category, amount or date? (c / a / d) ')
            if edit_choice.lower() not in ['c', 'a', 'd']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter c (category), a (amount) or d (date).')

    if edit_choice.lower() == 'c':
        # Display category options to the user
        print('')
        print(f'{"Index":<6}{"Category":<15}')
        for i, category in enumerate(CATEGORIES):
            print(f"{i+1:<6}{category:<15}")

        # Prompt user for new category index
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
        # Update the category for the selected expense
        selected_expense["Category"] = CATEGORIES[category_index]
        row_index = EXPENSES.find(selected_expense["Date"]).row
        EXPENSES.update_cell(row_index, 2, selected_expense["Category"])
        print('Category updated successfully')

        # Ask if user wants to edit more parameters
        while True:
            more_choice = input('\nDo you want to edit more parameters for this expense? (y/n) ')
            if more_choice.lower() == 'y':
                # Prompt user to choose what to edit
                while True:
                    try:
                        edit_choice = input('\nWould you like to edit the category, amount or date? (c / a / d) ')
                        if edit_choice.lower() not in ['c', 'a', 'd']:
                            raise ValueError()
                        break
                    except ValueError:
                        print('Invalid choice. Please enter c (category), a (amount) or d (date).')
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
                    # Update the category for the selected expense
                    selected_expense["Category"] = CATEGORIES[category_index]
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(row_index, 2, selected_expense["Category"])
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

                elif edit_choice.lower() == 'd':
                    # Get new date
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

                    # Update the date for the selected expense
                    # Get the row index for the selected expense
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    # Update the date for the selected expense
                    selected_expense["Date"] = str(date)
                    EXPENSES.update_cell(row_index, 3, selected_expense["Date"])
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
            more_choice = input('\nDo you want to edit more parameters for this expense? (y/n) ')
            if more_choice.lower() == 'y':
                # Prompt user to choose what to edit
                while True:
                    try:
                        edit_choice = input('\nWould you like to edit the category, amount or date? (c / a / d) ')
                        if edit_choice.lower() not in ['c', 'a', 'd']:
                            raise ValueError()
                        break
                    except ValueError:
                        print('Invalid choice. Please enter c (category), a (amount) or d (date).')
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
                    # Update the category for the selected expense
                    selected_expense["Category"] = CATEGORIES[category_index]
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(row_index, 2, selected_expense["Category"])
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

                elif edit_choice.lower() == 'd':
                    # Get new date
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

                    # Update the date for the selected expense
                    # Get the row index for the selected expense
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    # Update the date for the selected expense
                    selected_expense["Date"] = str(date)
                    EXPENSES.update_cell(row_index, 3, selected_expense["Date"])
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
                    print('Invalid date. Please enter a date in the past or today')
                    continue
                break
            except ValueError:
                print("Incorrect date format. Please enter a valid date in the format YYYY-MM-DD.")
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
            more_choice = input('\nDo you want to edit more parameters for this expense? (y/n) ')
            if more_choice.lower() == 'y':
                # Prompt user to choose what to edit
                while True:
                    try:
                        edit_choice = input('\nWould you like to edit the category, amount or date? (c / a / d) ')
                        if edit_choice.lower() not in ['c', 'a', 'd']:
                            raise ValueError()
                        break
                    except ValueError:
                        print('Invalid choice. Please enter c (category), a (amount) or d (date).')
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
                    # Update the category for the selected expense
                    selected_expense["Category"] = CATEGORIES[category_index]
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    EXPENSES.update_cell(row_index, 2, selected_expense["Category"])
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

                elif edit_choice.lower() == 'd':
                    # Get new date
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

                    # Update the date for the selected expense
                    # Get the row index for the selected expense
                    row_index = EXPENSES.find(selected_expense["Date"]).row
                    # Update the date for the selected expense
                    selected_expense["Date"] = str(date)
                    EXPENSES.update_cell(row_index, 3, selected_expense["Date"])
                    print('Date updated successfully')   

            elif more_choice.lower() == 'n':
                break
            else:
                print('Invalid choice. Please enter y (yes) or n (no).')

    go_back_edit_expense()

def year_statement():
    # Prompt user for year
    current_year = datetime.today().year
    while True:
        try:
            year = int(input(f'\nEnter year (1900 - {current_year}): '))
            if year < 1900 or year > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number between 1900 and {current_year} ')
    
    # Read expenses form Google Sheets document
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expenses for the chosen year
    
    total_expenses = {}
    for row in all_rows:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        if expense_date.year == year:
            category = row[1]
            amount = int(row[0])
            if category in total_expenses:
                total_expenses[category] += amount
            else:
                total_expenses[category] = amount

    # Print total expenses for all categories
    total_year_expense = sum(total_expenses.values())

    print(f"\nTotal expenses for all categories in {year}: ${total_year_expense}\n")
    for category, amount in total_expenses.items():
        print(f"{category}: ${amount}")
        print('')

    # Ask user if they want to see statement for another year
    while True:
        try:
            choice = input('\nDo you want to see another year statement? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        year_statement()
    else:
        return

    go_back_exp_year()

def month_statement():
    # Prompt user for year and month
    current_year = datetime.today().year
    while True:
        try:
            year = int(input(f'\nEnter year (1900 - {current_year}): '))
            if year < 1900 or year > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number between 1900 and {current_year} ')
    
    max_month = 12 if year < current_year else datetime.today().month
    while True:
        try:
            month = int(input(f'\nEnter month: (1 - {max_month}) '))
            if month < 1 or month > max_month:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between 1 and {max_month}. ')

    # Read expenses from Google Sheets document
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expenses for all categories in the chosen month and year
    total_expenses = {}
    for row in all_rows:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        if expense_date.year == year and expense_date.month == month:
            category = row[1]
            amount = int(row[0])
            if category in total_expenses:
                total_expenses[category] += amount
            else:
                total_expenses[category] = amount

    # Print total expenses for all categories
    total_month_expense = sum(total_expenses.values())
    print(f"\nTotal expenses for all categories in {month}/{year}: ${total_month_expense}\n")
    for category, amount in total_expenses.items():
        print(f"{category}: ${amount}")
        print('')

    # Ask user if they want to see statement for another year
    while True:
        try:
            choice = input('\nDo you want to see another year statement? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        month_statement()
    else:
        return

    go_back_exp_year()

def compare_year_expenses():
    # Prompt user for two years
    current_year = datetime.today().year
    while True:
        try:
            year1 = int(input(f'\nEnter first year to compare (1900 - {current_year}): '))
            if year1 < 1900 or year1 > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number between 1900 and {current_year} ')

    while True:
        try:
            year2 = int(input(f'Enter second year to compare (1900 - {current_year}): '))
            if year2 < 1900 or year2 > current_year:
                raise ValueError()
            if year2 == year1:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a different number between 1900 and {current_year}, excluding {year1}')

    # Read expenses form Google Sheets document
    all_rows = EXPENSES.get_all_values()[1:]

    # Calculate total expenses for for each year
    expenses_by_year = {}
    for row in all_rows:
        expense_date = datetime.strptime(row[2], '%Y-%m-%d')
        year = expense_date.year
        if year in expenses_by_year:
            expenses_by_year[year] += int(row[0])
        else:
            expenses_by_year[year] = int(row[0])

    # Calculate percentage difference between the two years
    if year1 in expenses_by_year and year2 in expenses_by_year:
        diff = expenses_by_year[year2] - expenses_by_year[year1]
        percent = abs(diff / expenses_by_year[year1] * 100)
        print(f"\nTotal expenses in {year1}: ${expenses_by_year[year1]}")
        print(f"Total expenses in {year2}: ${expenses_by_year[year2]}")
        if diff > 0:
            print(f"\nExpenses were lower in {year1} by ${diff:} ({percent:.2f}%)")
        elif diff < 0:
            print(f"\nExpenses were lower in {year2} by ${abs(diff):} ({percent:.2f}%)\n")
        else:
            print("\nExpenses were the same in both years")
    else:
        print("\nOne or both of the years are not in the expenses data")

    # Ask user if they want to see statement for another year
    while True:
        try:
            choice = input('\nDo you want to see another year statement? (y/n) ')
            if choice.lower() not in ['y', 'n']:
                raise ValueError()
            break
        except ValueError:
            print('Invalid choice. Please enter y (yes) or n (no).')

    if choice.lower() == 'y':
        compare_year_expenses()
    else:
        return

    go_back_compare_year()

def compare_month_expenses():
    # Prompt user for year and month for the first date
    current_year = datetime.today().year
    while True:
        try:
            year1 = int(input(f'\nEnter year for first date (1900 - {current_year}): '))
            if year1 < 1900 or year1 > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a number between 1900 and {current_year} ')

    while True:
        max_month = 12 if year1 < current_year else datetime.today().month
        try:
            month1 = int(input(f'\nEnter month for first date (1 - {max_month}) '))
            if month1 < 1 or month1 > max_month:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between 1 and {max_month}. ')

    # Show user picked first date
    print(f'\nFirst date to compare: {year1}/{month1}')

    # Prompt user for year and month for the second date
    while True:
        try:
            year2 = int(input(f'\nEnter year for second date (1900 - {current_year}): '))
            if year2 < 1900 or year2 > current_year:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid year. Please enter a different number between 1900 and {current_year}, excluding {year1}')

    while True:
        max_month = 12 if year2 < current_year else datetime.today().month
        try:
            month2 = int(input(f'\nEnter month for second date (1 - {max_month}) '))
            if month2 < 1 or month2 > max_month:
                raise ValueError()
            if year2 == year1 and month2 == month1:
                raise ValueError()
            break
        except ValueError:
            print(f'Invalid month. Please enter a number between 1 and {max_month}, exclude {year1}/{month1} you picked in the first date. ')

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
    total_month1_expenses = sum([expenses_by_month[category][0] for category in expenses_by_month])
    total_month2_expenses = sum([expenses_by_month[category][1] for category in expenses_by_month])

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
            print(f"\nExpenses were lower in {year1}/{month1} by ${diff:} ({percent:.2f}%)")
        elif diff < 0:
            print(f"\nExpenses were lower in {year2}/{month2} by ${abs(diff):} ({percent:.2f}%)\n")
        else:
            print("\nExpenses were the same in both months")
    else:
        print("\nThere were no expenses in the first month.")

    go_back_compare_month()

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

main()