#!/usr/bin/env python
"""get_year.py

This module contains a function that tries to
extract a four digit number from a string. If 
there is no four digit number in the string,
a blank is returned.
"""

import re

__author__ = "Martin Bolger"
__date__ = "February 28th, 2021"

def get_year(string):
    # Check to see if the string contains parentheses
    parentheses = re.search(r"[/(|/)]", string)
    if parentheses:
        # If it does, use the expression for matches inside of parentheses
        matches = re.search(r"\(((\w|\s)*((-|\/)\w*)?,? (\d*,\s)?)?((18|19|20)\d{2}\s?[-|,]?\s?((18|19|20)?\d{2})?\s?)\)", string)
        if matches:
            year = matches.group(6)
            # Standardize the output for the year variable
            year = re.sub(r"\s?[-|,]\s?", "-", year)
        else:
            year = ""
    else:
        # If it doesn't we just look for something that looks like it is a year
        matches = re.search(r"(19|20)\d{2}", string)
        if matches:
            year = matches.group(0)
        else:
            year = ""
    return year

if __name__ == "__main__":
    test_cases = ["14 Disp. Resol. Mag. 6 (Spring and Summer 2008)", "15 Am. Jurist & L. Mag. 321 (1836)", "6 Tex. S. U. L. Rev. 7 (1979,1981)", "2004 Duke L. & Tech. Rev. 0009", "6 Int'l Fin. L. Rev. 13 (December, 1987)", "32 Envtl. L. Rep. News & Analysis 10003 (2002)", "43 La. L. Rev. 1001 (1982-1983)", "test string (", "5 (September-October 2003)", "1-2 (Winter/Spring 2003)", "5 (May 2010 )", "85 W. Va. L. Rev. 187 (1982-83)", "6 Buff. Crim. L. Rev. 1043 (2002 - 2003)", "2001 Fed. Cts. L. Rev. 1"]
    for case in test_cases:
        year = get_year(case)
        print("Test case: {}".format(case))
        print("Year output: {}".format(year))