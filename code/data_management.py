#!/usr/bin/env python
"""data_management.py

This script performs the data management operations for the
Hein scraping data:
- The data is split into control and lateral groups
- Variables are renamed
- School URLs are merged onto the datasets
"""

import pandas as pd
import pathlib
from modules.create_path import create_path
from modules.get_school_urls import get_school_urls
from modules.short_url import short_url

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

# Create the paths for the data directories
input_path, work_path, intr_path, out_path, selenium_driver_path = create_path()

# -------------------------------------------------------------------------
## IMPORT: The dataset of professor names and the dataset of university and
## college websites.
# -------------------------------------------------------------------------

# Import the professor data
data = pd.read_excel(input_path / "prof_data_lateral_control.xlsx")

# Import the website data
# If we have already run the proram, we import the version form working
# If we have not run the program, we need to use the version from the 
# input directory
url_file = work_path / "university_and_college_websites.csv"
if url_file.exists():
    website_data = pd.read_csv(url_file)
else:
    url_file = input_path / "university_and_college_websites.csv"
    if url_file.exists():
        website_data = pd.read_csv(url_file)
    else:
        print("ERROR: The dataset of University and College Websites was not found in the input directory. Ending")
        quit()

# -------------------------------------------------------------------------
## DATA CLEANING professor data: We clean the variables that we need 
## from the professor data dataset and split the dataset into the 
## control and lateral groups.
# -------------------------------------------------------------------------

# DATA CLEANING: Remove commas from school names (e.g., University of Texas, Austin becomes University of Texas Austin)
data["Origin School"] = data["Origin School"].apply(lambda x: x.replace(',', '') if pd.notnull(x) else x)
data["Destination School"] = data["Destination School"].apply(lambda x: x.replace(',', '') if pd.notnull(x) else x)

# SUBSET: Drop columns that we won't be using
data = data.drop(["Origin US Law Sch", "BAYear", "JDYear", "PhD", "PhDYear", "BeganTeaching", "Gender", "Race", "OrigRank", "HiringRank"], axis = 1)

# DATA CLEANING: This line removes white space before or after names in the dataframe of names
data["FirstName"] = data["FirstName"].apply(lambda x: x.str.strip() if type(x) == "str" else x)
data["LastName"] = data["LastName"].apply(lambda x: x.str.strip() if type(x) == "str" else x)

# DATA CHECK: The lateral column should = 1 or 0 (for whether or
# not each observation is a lateral). We want to make sure it 
# doesn't take any other values.
data_types = set(data["Lateral"].to_list())

if not (1 in data_types and 0 in data_types and len(data_types) == 2):
    print("ERROR: The variable Lateral contains unexpected values. Ending")
    quit()

# SUBSET: Subset the data into two datasets: the lateral and control groups.
control = data[data["Lateral"] == 0]
lateral = data[data["Lateral"] == 1]

# DATA CHECK: Make sure that we did not drop any observations when 
# splitting into two datasets.
full_data_length = len(data.index)
control_length = len(control.index)
lateral_length = len(lateral.index)

if full_data_length != control_length + lateral_length:
    print("ERROR: The length of the data subsets does not equal the length of the dataset. Ending.")
    quit()

# -------------------------------------------------------------------------
## DATA CHECK: We search for all of the school names from the professor
## data in the school website list. If the school is not in the list,
## we search for the website and add it.
# -------------------------------------------------------------------------

# Create a path for the Chrome binary file. This is the executable file that
# is used to open Selenium.
chrome_binary_path = pathlib.Path("C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe")
selenium_driver_full_path = selenium_driver_path / "chromedriver.exe"

# Update the school URL list for the schools from the control dataset
website_data = get_school_urls(urls_df = website_data, 
                school_list = control["Origin School"], 
                browser_binary_path = chrome_binary_path, 
                selenium_driver_path = selenium_driver_full_path,
                output_path = work_path)

# Update the school URL list for the schools from the lateral dataset
website_data = get_school_urls(urls_df = website_data, 
                school_list = lateral["Origin School"], 
                browser_binary_path = chrome_binary_path, 
                selenium_driver_path = selenium_driver_full_path,
                output_path = work_path)

website_data = get_school_urls(urls_df = website_data, 
                school_list = lateral["Destination School"], 
                browser_binary_path = chrome_binary_path, 
                selenium_driver_path = selenium_driver_full_path,
                output_path = work_path)

# Create the short URL for each URL on the website data dataframe
website_data= short_url(url_data = website_data, url_var = "URL")

# Drop any duplicate entries on the dataset
website_data = website_data.drop_duplicates(subset = "School Name")

# DATA CHECK: Make sure that the data is unique by the school name
if website_data["School Name"].is_unique == False:
    print("ERROR: The University and College URL data is not unique by School Name. Ending.")
    quit()

# Save a copy of the website data
website_data.to_csv(work_path / 'university_and_college_websites.csv', index=False)

# -------------------------------------------------------------------------
## MERGE: Now merge the professor data and the website data.
## This merge is based on the school name.
# -------------------------------------------------------------------------

## Control data:
# Merge on origin school in the control data
control = pd.merge(website_data[["School Name", "Short URL"]], control, how = "right", left_on = "School Name", right_on = "Origin School")
# Drop the variable School Name
control = control.drop(["School Name"], axis = 1)
# RENAME: Rename the short URL column
control = control.rename(columns = {"Short URL": "Short URL Origin"})

## Lateral data:
# Merge on origin school in the lateral data
lateral = pd.merge(website_data[["School Name", "Short URL"]], lateral, how = "right", left_on = "School Name", right_on = "Origin School")
# Drop the variable School Name
lateral = lateral.drop(["School Name"], axis = 1)
# RENAME: Rename the short URL column
lateral = lateral.rename(columns = {"Short URL": "Short URL Origin"})
# Merge on destination school in the lateral data
lateral = pd.merge(website_data[["School Name", "Short URL"]], lateral, how = "right", left_on = "School Name", right_on = "Destination School")
# Drop the variable School Name
lateral = lateral.drop(["School Name"], axis = 1)
# RENAME: Rename the short URL column
lateral = lateral.rename(columns = {"Short URL": "Short URL Destination"})

#DATA CHECK: Make sure that there are no missing values for the short URL variables
if lateral["Short URL Destination"].isnull().values.any() == True or lateral["Short URL Origin"].isnull().values.any() == True or control["Short URL Origin"].isnull().values.any() == True:
    print("ERROR: There are missing values for the short url variable on one of the output datasets. Ending.")
    quit()

## EXPORT: Export the final control and lateral datasets
control.to_excel(work_path / "control.xlsx")
lateral.to_excel(work_path / "lateral.xlsx")
