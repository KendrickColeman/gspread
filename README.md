# gspread

This is a simple Python library for accessing Google Spreadsheets. The point is to make the API easier to use.

## Usage

~~~python
import gspread

gc = gspread.Client(auth=('the.email.address@gmail.com','password'))
gc.login()

# Spreadsheets can be opened by their title in Google Docs
spreadsheet = gc.open('some title')

# Select worksheet by index. Worksheet indexes start from zero
worksheet = spreadsheet.get_worksheet(0)

# Column and row indexes start from one
first_col = worksheet.col_values(1)

worksheet.update_cell(1, 2, 'Bingo!')
~~~
