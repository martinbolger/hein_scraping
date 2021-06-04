#!/usr/bin/env python
"""flag_unusual_names.py

Flag authors who have alt names
three or more alt names, have alt names
that start with an initial, or 
have alt names that start with a 
name that does not match the 
original first name
"""

import re 

def flag_unusual_names(alt_names, first_name):
    # Create a list of the alt names
    alt_name_list = alt_names.split(",")
    alt_name_list = [x.strip() for x in alt_name_list]

    flag = ""
    # Perform the data checks to see if we want to flag this name
    if len(alt_name_list) > 2:
        flag = "More than two names"
    for alt_name in alt_name_list:
        # Name starts with an initial
        if re.search(r"^\w\.\s", alt_name):
            flag = "Alt name starts with initial"
        # The alt_name first name does not match the first name from the original data
        if alt_name.split(" ")[0] != first_name:
            flag = "Alt name does not match the first name field"
    return flag