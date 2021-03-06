#!/usr/bin/env python
"""convert_roman_to_arabic.py

This module contains a function that 
converts Roman numerials to Arabic
numerials.
"""

import re

__author__ = "Martin Bolger"
__date__ = "March 06th, 2021"

def convert_roman_to_arabic(string):
    result = string
    # Check if the string is a valid roman numeral
    if bool(re.search(r"(^(?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$)",result, flags = re.I)) == True:
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
    output = convert_roman_to_arabic("xxx")
    print(output)
    output = convert_roman_to_arabic("xi")
    print(output)
    output = convert_roman_to_arabic("iv")
    print(output)
    