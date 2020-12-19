#!/usr/bin/env python
"""data_management.py

This script performs the data management operations for the
Hein scraping data:
- The data is split into control and lateral groups
- Variables are renamed
- School URLs are merged onto the datasets
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import bs4 as bs
import re
import time
from selenium.webdriver.common.keys import Keys
import nltk
import requests
import random
import math
import pathlib
from modules.create_path import create_path
from modules.get_school_urls import get_school_urls
from modules.short_url import short_url

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

# Create the paths for the data directories
input_path, work_path, intr_path, out_path, selenium_driver_path = create_path()

# Import the dataset of professor names
data = pd.read_excel(input_path / "prof_data_lateral_control.xlsx")

# Import the dataset of university and college websites
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

print(website_data.head())
print(website_data.tail())


#This line inserts the urls into the full dataframe
# new_data.insert(4, "School URL", url_list) 
# # The function returns the short version of the URLs
# url_list = short_url(new_data['School URL'])
# # This line inserts the short version of the URLs into the dataframe
# new_data.insert(5, "School URL short", url_list)
# #This section repeats the same steps for the second set of schools
# print('First half complete')
# url_list = get_school_urls(urls, new_data['New School'])
# new_data.insert(7, "New School URL", url_list) 
# url_list = short_url(new_data['New School URL'])
# new_data.insert(8, "New School URL short", url_list) 
# new_data.head()

control.to_excel(work_path / "control.xlsx")
lateral.to_excel(work_path / "lateral.xlsx")
