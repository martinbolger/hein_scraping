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



