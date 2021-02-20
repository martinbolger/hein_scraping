#!/usr/bin/env python
"""create_final_paper_list.py

This script combines all of the files that
are output by the hein_paper_scraping
script. The citation date and journal name 
are also extracted from the papers.
"""

import pandas as pd
import os
import pathlib
import re
from modules.create_path import create_path
from modules.get_journal_data import get_journal_data
from modules.get_year import get_year

__author__ = "Martin Bolger"
__date__ = "December 26th, 2020"

# Create the paths for the data directories
input_path, work_path, intr_path, out_path, selenium_driver_path = create_path()

# Stack the output files
files = os.listdir(out_path)
stacked_output = pd.DataFrame()
for f in files:
    # If the name of the file does not start with "_", it is one 
    # of the scraped data files.
    if f[0] != "_":
        data = pd.read_excel(out_path / f, 'Sheet1')
        data["file"] = f
        stacked_output = stacked_output.append(data)

# Rename the stacked output as df
df = stacked_output

# SORT: Sort the dataset by ID
stacked_output.sort_values(by = ["ID"], inplace = True)

# Drop rows where the author name is "na". These come from
# Papers that are on an author's page that do not contain 
# the author's last name. If observations that are not
# duplciates are in this category, you should look to see
# if the author's last name changed.

stacked_output["dup_title"] = stacked_output["Title"].duplicated(keep=False)

stacked_output["na_author"] = stacked_output["Author(s)"].apply(lambda x: True if x == "na" else False)

# stacked_output.to_excel(out_path / "_stacked_output.xlsx")

# Confirm that every time the author is "na", the observation is a duplicate.
if not stacked_output[(stacked_output["na_author"] == True) & (stacked_output["dup_title"] == False)].empty:
    print("ERROR: There are observations with no author that are not duplicates. Please check for authors with multiple last names. Ending.")
    quit()


# Subset to non-duplicates
stacked_output = stacked_output.drop(["file", "dup_title"], axis = 1).drop_duplicates()

# Add a flag so that we can make sure that there are no other duplicates.
stacked_output["dup_all"] = stacked_output.duplicated()

# # Now that we know that all observations with a missing author name are duplicates, we can remove them.
# stacked_output = stacked_output[(stacked_output["na_author"] == False) | (stacked_output["dup_title"] == False)]

# Drop na flag
stacked_output = stacked_output.drop(["na_author"], axis = 1)

df = stacked_output

# Extract paper type
df.insert(1, "Paper Type", [x.split('[')[-1].split(']')[0] if '[' in x else '' for x in df['Title']])

# Remove paper type from title
df['Title'] = [x.split(' [')[-2] if '[' in x else x for x in df['Title']]

# BBCite year
df['BBCite'] = df['BBCite'].str.replace('Full Text Not Currently Available in HeinOnline', '')
df["BBCite Year"] = df['BBCite'].apply(lambda x: get_year(x))
# Number of Authors
df.insert(4, 'Number of Authors', [x.count(';') + 1 for x in df['Author(s)']])

#Replace na in Cited and Accessed columns:
df['Cited (articles)'] = df['Cited (articles)'].astype(str)
df['Cited (cases)'] = df['Cited (cases)'].astype(str)
df['Accessed'] = df['Accessed'].astype(str)
df['Cited (articles)'] = df['Cited (articles)'].str.replace('na', '0')
df['Cited (cases)'] = df['Cited (cases)'].str.replace('na', '0')
df['Accessed'] = df['Accessed'].str.replace('na', '0')
df['Accessed'].astype('int')
df['Cited (cases)'].astype('int')
df['Cited (articles)'].astype('int')
df['ID'].astype('int')

# Replace na in Journal, Topics, and BBCite columns
df['Journal'] = [re.sub(r'\bna\b', '', x) for x in  df['Journal']]
df['Topics'] = [re.sub(r'\bna\b', '', x) for x in  df['Topics']]
df['Subjects'] = [re.sub(r'\bna\b', '', x) for x in  df['Subjects']]
df['BBCite'] = [re.sub(r'\bna\b', '', x) for x in  df['BBCite']]

# Use the get_journal_data function to extract the journal data
df = get_journal_data(df)

# Calculate the issue year
issue_year_list = df["Issue"].apply(lambda x: re.search(r"\d{4}", x))
df["Issue Year"] = issue_year_list.apply(lambda x: x.group(0) if x else '')

# Extract the first and last page for each paper
df["First Page"] = df["Pages"].apply(lambda x: x.split('-')[0] if '-' in x else '')
df["Last Page"] = df["Pages"].apply(lambda x: x.split('-')[1] if '-' in x else '')

# Output the stacked paper data
df.to_excel(out_path / "_stacked_paper_data.xlsx")