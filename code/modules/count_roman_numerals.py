#!/usr/bin/env python
"""count_roman_numerals.py

This module contains a function that 
counts the number of Roman numerals
in the page number span.
"""

import re

__author__ = "Martin Bolger"
__date__ = "March 06th, 2021"

def count_roman_numerals(first_page, last_page):

    count = 0
    # Check if the string is a valid roman numeral
    if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", first_page, flags = re.I)) == True:
        count += 1
    if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", last_page, flags = re.I)) == True:
        count += 1
        
    # Return the count
    return count

if __name__ == "__main__":
    output = count_roman_numerals("iv", "v")
    print("Count: {}".format(output))
    output = count_roman_numerals("4", "v")
    print("Count: {}".format(output))
    output = count_roman_numerals("iv", "5")
    print("Count: {}".format(output))

    