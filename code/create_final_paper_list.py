#!/usr/bin/env python
"""create_final_paper_list.py

This script combines all of the files that
are output by the hein_paper_scraping
script. The citation date and journal name 
are also extracted from the papers.
"""

import pandas as pd
import numpy as np
import os
import pathlib
import re
from modules.create_path import create_path
from modules.get_journal_data import get_journal_data
from modules.get_year import get_year
from modules.flag_author_cut_off import flag_author_cut_off
from modules.clean_page_number import clean_page_number

__author__ = "Martin Bolger"
__date__ = "February 28th, 2021"

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

# Flag papers with duplicate titles
stacked_output["dup_title"] = stacked_output.duplicated(subset = ["Title"], keep= False)

# Confirm that every time the author is "na", the observation is a duplicate.
if not stacked_output[(stacked_output["Author(s)"] == "na") & (stacked_output["dup_title"] == False)].empty:
    print("ERROR: There are observations with no author that are not duplicates. Please check for authors with multiple last names. Ending.")
    quit()

# Drop all entries that have a missing author "na". These entires 
# are added when we have an author with multiple last names. Their
# page may be scrapped twice. We only save the author name when
# it is the name that we are looking for to avoid duplicates.
stacked_output = stacked_output.loc[stacked_output["Author(s)"] != "na"].copy()

# We can still get duplicates if the author has multiple first names and
# multiple last names because the page has to be scrapped for each first name/last name
# combination. We can drop these duplicates by the title of the paper and the author name.
stacked_output["duplicate_title_author"] = stacked_output.duplicated(subset = ["Title", "Author(s)", "Journal", "BBCite"], keep= "first")

# Drop the duplicate entries
stacked_output = stacked_output[stacked_output["duplicate_title_author"] == False].copy()

# stacked_output.to_excel(out_path / "_stacked_output.xlsx")

# Drop na flag
stacked_output = stacked_output.drop(["duplicate_title_author", "dup_title"], axis = 1)

df = stacked_output

# Extract paper type
df.insert(1, "Paper Type", [x.split('[')[-1].split(']')[0] if '[' in x else '' for x in df['Title']])

# Remove paper type from title
df['Title'] = [x.split(' [')[-2] if '[' in x else x for x in df['Title']]

# BBCite year
df['BBCite'] = df['BBCite'].str.replace('Full Text Not Currently Available in HeinOnline', '')
df["BBCite Year"] = df['BBCite'].apply(lambda x: get_year(x))

# Get the first BBCite year
bbcite_year_list = df['BBCite Year'].apply(lambda x: re.search(r"\d{4}", x))
df["BBCite Year First"] = bbcite_year_list.apply(lambda x: x.group(0) if x else '')
df['BBCite Year First'] = df['BBCite Year First'].replace('', "9999").astype("int")
df["Before 1963 Flag"] = df["BBCite Year First"].apply(lambda x: 1 if x < 1963 else 0)

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
df["First Page"] = df["Pages"].apply(lambda x: clean_page_number(x.split('-')[0]) if '-' in x else '')
df["Last Page"] = df["Pages"].apply(lambda x: clean_page_number(x.split('-')[1]) if '-' in x else '')

# Add the author flags using the author cut-off data
cut_off_data = pd.read_excel(
    input_path / "author_year_cut_offs_control.xlsx", 
    'Sheet1'
)

# # Merge the cut-off data with the main dataset
merge_test = pd.merge(
    df,
    cut_off_data,
    how = "left",
    left_on = "ID",
    right_on = "ID",
    sort = "False"
)

# Convert the types for string vars and change nan to ""
merge_test["Word Exclude"] = merge_test["Word Exclude"].astype(str)
merge_test['Word Exclude'] = merge_test['Word Exclude'].str.replace('nan', '')
merge_test["BBCite Exclude"] = merge_test["BBCite Exclude"].astype(str)
merge_test['BBCite Exclude'] = merge_test['BBCite Exclude'].str.replace('nan', '')
merge_test["Journal Exclude"] = merge_test["Journal Exclude"].astype(str)
merge_test['Journal Exclude'] = merge_test['Journal Exclude'].str.replace('nan', '')

merge_test["author_exclusion_flag"] = merge_test.apply(lambda x: flag_author_cut_off(x["Start Year"], x["BBCite Year First"], x["Journal Exclude"], x["Journal Name"], x["Word Exclude"], x["Title"], x["BBCite Exclude"], x["BBCite"]), axis = 1)

# Subset to the rows that are not flagged by the author exclusion flag
merge_test = merge_test[merge_test["author_exclusion_flag"] == 0]

# Subset to the rows that are not flagged by before 1963 flag
merge_test = merge_test[merge_test["Before 1963 Flag"] == 0]

# Drop extra variables
merge_test = merge_test.drop(["Start Year",	"Journal Exclude", "Word Exclude", "BBCite Exclude", "author_exclusion_flag", "BBCite Year First", "Before 1963 Flag", 'First Name', 'Last Name'], axis = 1)

# Reorder the columns
merge_test = merge_test[['ID', 'Title', 'Paper Type', 'Author(s)', 'Number of Authors', 'Journal', 'BBCite', 'BBCite Year', 'Topics', 'Subjects', 'Cited (articles)', 'Cited (cases)', 'Accessed', 'Journal Name', 'Vol', 'Issue', 'Pages', 'Issue Year', 'First Page', 'Last Page']]

# Convert numeric columns to numbers
merge_test[["Number of Authors", "Cited (articles)", "Cited (cases)", "Accessed"]] = merge_test[["Number of Authors", "Cited (articles)", "Cited (cases)", "Accessed"]].astype(int)

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(out_path / "_stacked_paper_data_control.xlsx", engine='xlsxwriter')  # pylint: disable=abstract-class-instantiated

# Convert the dataframe to an XlsxWriter Excel object.
merge_test.to_excel(writer, sheet_name='Sheet1')

# Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

# Add some cell formats.
format2 = workbook.add_format({'num_format': '#'})

# Note: It isn't possible to format any cells that already have a format such
# as the index or headers or any cells that contain dates or datetimes.

# Set the column width and format.
worksheet.set_column('F:F', 18, format2)

# Close the Pandas Excel writer and output the Excel file.
writer.save()

# merge_test.to_excel(out_path / "_stacked_paper_data_control.xlsx")
