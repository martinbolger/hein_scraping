#!/usr/bin/env python
"""clean_page_number.py

This module contains a function that cleans
page numbers so that they are all formatted
as regular numbers.
"""

import re

__author__ = "Martin Bolger"
__date__ = "February 28th, 2021"

def clean_page_number(string):
    result = re.sub(r"[\[|\]|S]", "", string)

    # Check if the string is a valid roman numeral
    if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$",result, flags = re.I)) == True:
        # Convert it to an Arabic numeral if it is
        rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        # Make sure that the Roman numeral is uppercase
        result = result.upper()
        int_val = 0
        for i in range(len(result)):
            if i > 0 and rom_val[result[i]] > rom_val[result[i - 1]]:
                int_val += rom_val[result[i]] - 2 * rom_val[result[i - 1]]
            else:
                int_val += rom_val[result[i]]
        result = int_val

    # Return the formatted page number
    return result

if __name__ == "__main__":
    output = clean_page_number("[45]")
    print(output)
    output = clean_page_number("S1324")
    print(output)
    output = clean_page_number("iv")
    print(output)
    