#!/usr/bin/env python
"""article_in_bbcite_control.py

This module contains a function that tries to
flag potential article names in the BBCite field.
"""

import re

__author__ = "Martin Bolger"
__date__ = "February 28th, 2021"

def article_in_bbcite(string):
    # Search for entries that start with a letter (BBCites should start with a number)
    matches = re.search(r"^[a-zA-z]", string)
    if matches:
        flag = 1
    else:
        flag = 0
    return flag

if __name__ == "__main__":
    test_cases = ["6 Tex. S. U. L. Rev. 7 (1979,1981)", "2004 Duke L. & Tech. Rev. 0009", "Understanding the Ex Parte Communications Ban in Employment Disputes [article]"]
    for case in test_cases:
        flag = article_in_bbcite(case)
        print("Test case: {}".format(case))
        print("Test output: {}".format(flag))