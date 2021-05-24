#!/usr/bin/env python
"""alt_name_modifiction.py

This script modifies the list of alternate names
that is output by the alt_name_data_creation
script. It does this by merging the full alt names
list with the name modifiction dataset and comparing
the list of names in each dataset.
"""

import pandas as pd
import pathlib
from modules.create_path import create_path
from modules.data_manipulation_functions import concat_function, remove_err_names

__author__ = "Martin Bolger"
__date__ = "December 25th, 2020"

# Create the paths for the data directories
input_path, work_path, intr_path, out_path, selenium_driver_path = create_path()

# Set the data type
data_type = "lateral"

# Load the name modification dataset
# This is a dataframe of names that we want to manually change 
# This can be used if we found errors in the data (for example, names were not scraped)
# This dataset is edited by hand, so it is stored in the input directory
name_mod = pd.read_excel(input_path / 'name_mod_{}.xlsx'.format(data_type))

# Load the full alt name dataset. This is the output of 
# the alt name dataset creation script.
alt_name_full = pd.read_excel(intr_path / "alt_names.xlsx")

# MERGE: Merge on the name mod dataset
alt_name_mod_name = pd.merge(alt_name_full, name_mod[["ID", "fm_names", "err_fm_names", "alt_url"]], how = "left", left_on = ["ID"], right_on = ["ID"], suffixes=('_orig', '_mod'))

# Concatenate the values from the alternate name and name mod dataframes
alt_name_mod_name["fm_names"] = alt_name_mod_name.apply(lambda x: concat_function(x["fm_names_orig"], x["fm_names_mod"]), axis = 1) 
# alt_name_mod_name["err_fm_names"] = alt_name_mod_name.apply(lambda x: concat_function(x["err_fm_names_orig"], x["err_fm_names_mod"]), axis = 1)

# Replace nan values with a blank string so that we can run the function remove_err_names
alt_name_mod_name["fm_names"].fillna('', inplace=True)
alt_name_mod_name["err_fm_names_mod"].fillna('', inplace=True)

# Remove error names from the mod dataset from the list of names
alt_name_mod_name["fm_names"] = alt_name_mod_name.apply(lambda x: remove_err_names(x["fm_names"], x["err_fm_names_mod"]), axis = 1)

# Set the alt url column to 0 if it is blank
alt_name_mod_name["alt_url"] = alt_name_mod_name["alt_url"].apply(lambda x: 0 if pd.isnull(x) else x).astype(int)

alt_name_mod_name.to_excel(work_path / "alt_name_mod_name_full_vars.xlsx")

# DROP: Drop the duplicate columns from the alternate name and name mod dataframes.
# The err_fm_names column is also dropped because it is not used. This column can 
# be used to see which names we did not find on Hein in the above dataset.
alt_name_mod_name = alt_name_mod_name.drop(["fm_names_orig", "err_fm_names_orig", "fm_names_mod", "err_fm_names_mod"], axis = 1)

# Drop unnamed columns
alt_name_mod_name.drop(alt_name_mod_name.columns[alt_name_mod_name.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

# SORT: Sort the output data by ID
alt_name_mod_name.sort_values(["ID", "LastName"], inplace = True)

# Add an index for the number of duplicates for each name
alt_name_mod_name["ID_counts"] = alt_name_mod_name.groupby(["ID"]).cumcount()+1

# Output to Excel
alt_name_mod_name.to_excel(intr_path / "hein_scraping_input_data.xlsx", index = False)

print(alt_name_mod_name.head())
