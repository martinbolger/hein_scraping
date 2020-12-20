#!/usr/bin/env python

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

def list_to_comma_separated_string(list_of_strings):
    list_str = ', '.join(list_of_strings)
    list_str = list_str.replace('\'', '')
    list_str.replace('\"', '')
    return list_str