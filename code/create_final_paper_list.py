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

# Extract paper type
df.insert(1, "Paper Type", [x.split('[')[-1].split(']')[0] if '[' in x else '' for x in df['Title']])

# Remove paper type from title
df['Title'] = [x.split(' [')[-2] if '[' in x else x for x in df['Title']]

# BBCite year
df['BBCite'] = df['BBCite'].str.replace('Full Text Not Currently Available in HeinOnline', '')
df.insert(6, 'BBCite Year', [re.sub("[^0-9]", "", x.split('(')[1].split(')')[0])[:4] if '(' in x else '' for x in df["BBCite"]])
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
df['BBCite'] = [re.sub(r'\bna\b', '', x) for x in  df['BBCite']]

# Use the get_journal_data function to extract the journal data
df_j = get_journal_data(df)
# Calculate the issue year and first and last page for the journal
df_j.insert(3, 'Issue Year', [re.sub("[^0-9]", "", x.split('(')[1].split(')')[0])[:4] if '(' in x else '' for x in df_j["Issue"]])
df_j.insert(4, 'First Page', [x.split('-')[0] if '-' in x else '' for x in df_j['Pages']])
df_j.insert(5, 'Last Page', [x.split('-')[1] if '-' in x else '' for x in df_j['Pages']])


df_j.drop(["ID"], axis = 1, inplace = True)

print(df_j.head())
# MERGE: Merge the journal data onto the stacked data
stacked_df = pd.concat([df.reset_index(drop = True), df_j.reset_index(drop = True)], axis = 1)



# df_j.to_excel(out_path / "_journal_data.xlsx")
stacked_df.to_excel(out_path / "_stacked_paper_data.xlsx")

# stacked_output.to_excel(out_path / '_stacked_output.xlsx', index=False)