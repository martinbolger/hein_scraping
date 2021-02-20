#!/usr/bin/env python
"""get_year.py

This module contains a function that tries to
extract a four digit number from a string. If 
there is no four digit number in the string,
a blank is returned.
"""

import re

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

def get_year(string):
    matches = re.search(r"\((\w*((-|/)\w*)? (\d*,\s)?)?((19|20)\d{2}-?((19|20)\d{2})?\s?)\)", string)
    if matches:
        year = matches.group(5)
    else:
        year = ""
    return year

if __name__ == "__main__":
    year = get_year("32 Envtl. L. Rep. News & Analysis 10003 (2002)")
    print(year)
    year = get_year("43 La. L. Rev. 1001 (1982-1983)")
    print(year)
    year = get_year("test string (")
    print(year)
    year = get_year("5 (September-October 2003)")
    print(year)
    year = get_year("1-2 (Winter/Spring 2003)")
    print(year)
    year = get_year("5 (May 2010 )")
    print(year)