#!/usr/bin/env python
"""split_page_number.py

This module contains a function that splits
the page number field.

index = 1 or 2. This is for returning the
first or second page number.
"""

import re

__author__ = "Martin Bolger"
__date__ = "February 28th, 2021"

def split_page_number(string, index):
    page = ""
    # Make sure that the page number index is 1 or 2.
    if index not in [1, 2]:
        raise ValueError('Parameter should be equal to 1 or 2.')
    if string.count("-") == 1:
        if '-' in string:
            if index == 1:
                page = string.split('-')[0] 
            elif index == 2:
                page = string.split('-')[1] 
    elif string.count("-") == 2:
        match = re.match(r"(\[?(i|v|x|c|l)*\]?|\d*)-(\[?(i|v|x|c|l)*\]?|\d*)-(\d*|\[?(i|v|x|c|l)*\]?)$", string)
        if match:
            if index == 1:
                page = match.group(1)
            elif index == 2:
                page = match.group(5)
    elif string.count("-") == 3:
        match = re.match(r"(\d*-?(\d*))-(\d*-?(\d*))", string)
        if match:
            if index == 1:
                page = match.group(2)
            elif index == 2:
                page = match.group(4)
    return page

if __name__ == "__main__":
    first_page = split_page_number("6-1-6-10", 1)
    print("First page: {}".format(first_page))
    last_page = split_page_number("6-1-6-10", 2)
    print("Last page: {}".format(last_page))
    last_page = split_page_number("6-10", 2)
    print("Last page: {}".format(last_page))
    first_page = split_page_number("1048-1050-1052", 1)
    print("First page: {}".format(first_page))
    last_page = split_page_number("1048-1050-1052", 2)
    print("Last page: {}".format(last_page))
    first_page = split_page_number("1-1-[iv]", 1)
    print("First page: {}".format(first_page))
    last_page = split_page_number("1-1-[iv]", 2)
    print("Last page: {}".format(last_page))