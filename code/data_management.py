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
import os
import numpy as np
import re
import time
from selenium.webdriver.common.keys import Keys
import nltk
import requests
import random
import math
import pathlib
from modules.create_path import create_path

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

# Create the paths for the data directories
input_path, work_path, intr_path, out_path = create_path()

# Import the dataset
data = pd.read_excel(input_path / "prof_data_lateral_control.xlsx")

# DATA CHECK: The lateral column should = 1 or 0 (for whether or
# not each observation is a lateral). We want to make sure it 
# doesn't take any other values.
data_types = set(data["Lateral"].to_list())

if not (1 in data_types and 0 in data_types and len(data_types) == 2):
    print("ERROR: The variable Lateral contains unexpected values. Ending")
    quit()

# SUBSET: Subset the data into two datasets: the lateral and control groups
control = data[data["Lateral"] == 0]
lateral = data[data["Lateral"] == 1]

# DATA CHECK: Make sure that we did not drop any observations when 
# splitting into two datasets
full_data_length = len(data.index)
control_length = len(control.index)
lateral_length = len(lateral.index)

if full_data_length != control_length + lateral_length:
    print("ERROR: The length of the data subsets does not equal the length of the dataset. Ending.")
    quit()

control.to_excel(work_path / "control.xlsx")
lateral.to_excel(work_path / "lateral.xlsx")
