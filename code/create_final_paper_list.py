#!/usr/bin/env python
"""create_final_paper_list.py

This script combines all of the files that
are output by the hein_paper_scraping
script. The citation date and journal name 
are also extracted from the papers.
"""

import pandas as pd
import pathlib
from modules.create_path import create_path
from modules.data_manipulation_functions import concat_function, remove_err_names

__author__ = "Martin Bolger"
__date__ = "December 26th, 2020"