# Personal Expense Tracker

Personal Expense Tracker is an app to manage your expenses - the application stores data in Google Sheets documents. Users can add new costs based on 15 different expense categories, edit existing payments and do some statistics based on existing statistics, like see the year on a monthly statement or compare two years or two monthly reports.

[Here is the live version of my project](https://expense-tracker-app.herokuapp.com/)

![live_version](https://user-images.githubusercontent.com/119242394/229491565-58a0ef95-6435-460d-ad10-1bd9241d302c.png)

## User Manual

The application is written in Python command-line code. After a run, the user can pick the needed feature by entering the correct number on the console and pressing Enter. The application is user-friendly and intuitive. After each operation app asks the user what the user wants to do next, the user can choose to do more operations in the picked feature, go back to the main menu and select another one or exit the program. Every question users see on the screen describes and shows how to write more complex numbers, such as a correct date format, or numbers range. New or edited data is synchronized with Google Sheets documents automatically, and the user is informed on the screen.

## Features

### Existing Features

- Add a new expense feature
  - Users can choose one of the 15 expense categories. When the user enters numbers besides 1-15, a user is informed to choose a number from the correct range. This field needs to be filled.
  - User can enter expense amount. The amount has to be a positive number. When the user writes a float number, the application automatically rounds the number. This field needs to be filled.
  - User can enter expense date in the correct format. When the user picks a future date, the application asks the user to join past or today's date. The user is asked to do the format again when the format is incorrect. This field needs to be filled.

![add_expense_01](https://user-images.githubusercontent.com/119242394/229900090-9351707b-c0b3-46d6-b290-e5df731ce904.png) ![add_expense_02](https://user-images.githubusercontent.com/119242394/229900118-b846f759-d986-4c4e-b33f-08f356491375.png)

  
- Edit existing expense feature
  - User can edit existing expenses. When a user chooses to edit cost, he is asked to enter the expense's year and month
  - The user can choose an expense to edit by entering the correct number into the console
  - After that, a user is asked which parameter the user wants to change: "c", "a", or "d"
  - "c" is the category shortcut, "a" is the amount shortcut, and "d" is a date shortcut
  - After changing the picked expense's parameter, a user is asked if a user wants to change another parameter of the same expense
  - The user can choose another expense date if the user wants to or exit to the main menu

![edit_expense_01](https://user-images.githubusercontent.com/119242394/229901117-93003239-3568-4f21-8a92-221e42c51764.png)

- Show year statement feature
  - User can see how many expenses the user had in each year by entering expense year into the console
  - User sees total year amount and how many each categories expenses user had in the chosen year

![year_statement_01](https://user-images.githubusercontent.com/119242394/229901827-b8aaf781-0710-4acb-b8c8-27c875d01365.png)


- Show monthly statement feature
  - User can see how many expenses the user had in each month by entering expense year and month into the console
  - User sees total month amount and how many each categories expenses user had in the chosen month

![month_statement_01](https://user-images.githubusercontent.com/119242394/229902159-1be0c800-ef0e-44a0-95ca-6391d869be12.png)

- Compare two years feature
  - User can compare two expenses years
  - To compare two expenses year, a user has to enter the first year and the second year, wants to check, to the console
  - The second year has to be different from the first one
  - User sees expenses total amount for each year and can notice which year was lower in percent
  - User can see the total amount of each category of each picked year

![year_compare_01](https://user-images.githubusercontent.com/119242394/229902647-771e687e-22ff-4669-98e5-cdb02ee84c04.png)
![year_compare_02](https://user-images.githubusercontent.com/119242394/229902667-5e6c9795-3131-4cde-8af7-a0d3a3935a68.png)

- Compare two months feature
  - User can compare two expenses months
  - To compare two expenses month, a user has to enter the first year, the first month, and the second year, the second month, wants to check, to the console
  - The second month has to be different from the first one. If it's not user is asked to choose another second year and second month and try again
  - User sees expenses total amount for each month and can notice which year was lower in percent
  - User can see the total amount of each category of each picked month

![month_compare_01](https://user-images.githubusercontent.com/119242394/229903300-55140e64-021f-44ba-ba93-37826265c28b.png)

### Future Features
- Add monthly income to be more precise with future savings estimation 
- Add AI learning to predict categories user can save money
- Rewrite code to iOS and Android application

## Data Model
- The personal expense tracker stores data in a Google Sheet document, organized by three values: expense amount, expense category, and expense date.
- The application offers 15 expense categories: Housing, Transportation, Food, Utilities, Clothing, Healthcare, Insurance, Supplies, Personal, Debt, Retirement, Education, Savings, Gifts, and Entertainment. These categories are based on Recommended Budgeting Categories from [localfirstbank.com](https://localfirstbank.com/article/budgeting-101-personal-budget-categories/)
- The user interface is intuitive, guiding users to input the appropriate number from a given list of options for each step.

## Testing
I have manually tested this project by doing the following:
- Passed the code through a PEP8 linter and confirmed there are no problems
- Tested in my local terminal and the Code Institute Heroku terminal

### Bugs
- During the code writing process, I included many comments, descriptions, and functions that exceeded 80 characters in length. As a result, debugging was more challenging.
- Additionally, there were instances where only one line space was used between functions, which I had to correct to improve code readability.

### Remaining Bugs
- No bugs remaining

### Validator Testing
- PEP8
  - No errors were returned from [POP8](https://pep8ci.herokuapp.com/)

![python_test](https://user-images.githubusercontent.com/119242394/229908393-891ebc80-681c-45e3-a6fe-fe40af5443ac.png)

## Deployment
The project was deployed using Heroku.

- Steps for deployment:
  - Fork or clone this repository
  - Create a new Heroku app
  - Set the buildpacks to Python and NodeJS in that order
  - Link the Heroku app to the repository
  - Click on Deploy

## Credits
- [localfirstbank.com](https://localfirstbank.com/article/budgeting-101-personal-budget-categories/)
- [google.com](https://www.google.pl/)
