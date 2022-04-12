ISOTOPES IN PRECIPITATION - STATISTICS


INPUT
Excel files containing data on isotope composition of precipitation (default file in map 'data')

WHAT IS CALCULATED
- means (annual, mothly and seasonal)
- regression coefficients describing local meteoric water line (total and annual)


INSTRUCTIONS

Excel files:
- excel files must be in folder 'data'
- excel files must be constructed in a specific manner in order for program to work - an example data sheet can be found in the 'data' folder. 
- there should be only one 'sheet' in excel file
- the program supports the following type of excel files: xls 
- the names of excel files must be without dots (e.g. St. Petersburg -> St Petersburg)
- in excel file there should be dots (not commas) used for writing decimal numbers
- if no errors, the results will be saved in /results/<name_of_input_excel_file>
-

Start the program:
- make sure you have installed python3 on your computer, with the following libraries:
    - xlrd (version >= 2.1.0)
    - numpy
    - matplotlib.pyplot

- open the terminal at the location of README.txt and type in:
    $   python ISO.py     (to start the program)
    - after executing the program the command prompt will ask you to:
        - specify the name of the excel file, located in folder 'data' (e.g. Ljubljana16-18)
        - specify if precipitation amount data exists for all months ( * )
        - specify which types of statistics you want to calculate


Filters:
- if, for a given year, there is less than 8 (out of 12) existing values for some type of data, the annual statistics won't be made for this type of data (e.g. delta^18 O has missing data in year 2020 for months Jan-May -> only 7/12 values for the year 2020 -> the annual (2020) delta^18 O statistics won't be calculated)
- if, for a given year, the existing data (some type of data) represent less than 70% of total annual precipitation, the annual statistics won't be made for this type of data (e.g. only 10/12 data for delta^18 O are available for the year 2020, but this represents less than 70% of all precipitation collected that year -> the annual (2020) delta^18 O statistics won't be calculated)
- when calculating regression coefficients if one of the pair (delta^18 O, delta^2 H) is missing, then this pair of values won't be taken into account when calculating regression coefficients
- for given data (delta^18 O, delta^2 H), at least two years must be valid according to the above stated filters, for annual regression calculation to be executed
- in the case when all precipitation data is not available ( * ), the '70% filter' will not be taken into account and the weighted statistics will not be calculated

Rounding:
- by default the results are rounded on:
    2 decimals (delta^18 O)
    1 decimal (delta^2 H)
    1 decimal (deuterium)
    1 decimal (delta^3 H)
    2 decimals (regression coeffs.)
- note: rounding is done with python's function round, which rounds *.**n5 down to *.**n  (and not to *.**(n+1)* e.g. 2.675 is rounded to 2.67 and not to 2.68)   






Prepared by Aljaž Pavšek, IJS, 2022
# Isotopes-in-precipitation-statistics
