#!/usr/bin/env python

import pandas as pd

#Removes commas from all values in a row of a dataframe
def remove_commas(df1):
    for col in df1.columns:
        df1[col] = df1[col].str.replace(',', '')
    return df1

#This function checks to see if a file with the papers from a professor has already been created
#If it has, their name is skipped (their data is not rescraped)
def check_files(fm_name, last_name, current_files):
    done = False
    for cur_file in current_files:
        if fm_name.lower() in cur_file.lower() and last_name.lower() in cur_file.lower():
            done = True
            break
    return done

# This function converts a list of strings to a comma
# separated string.
def list_to_comma_separated_string(list_of_strings):
    list_str = ', '.join(list_of_strings)
    list_str = list_str.replace('\'', '')
    list_str.replace('\"', '')
    return list_str

# This function is used to concatenate strings
# in a panda dataframe. It can handle cases when
# one of the strings is missing. It is used in an 
# apply statement.
def concat_function(x, y):
    if not pd.isna(x) and not pd.isna(y):
        return x + ", " + y
    elif not pd.isna(x):
        return x
    elif not pd.isna(y):
        return y
    else:
        return x

# This function removes substrings from one list of 
# comma separated strings from another list. It is used
# to remove error names from the alt names lists.
def remove_err_names(names, err_names):
    if names:
        names_list = names.split(", ")
    else:
        names_list = []
    if err_names:
        err_names_list = err_names.split(", ")
    else:
        err_names_list = []
    names_list = [x for x in names_list if x not in err_names_list]
    return list_to_comma_separated_string(names_list)