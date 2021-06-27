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
from modules.convert_roman_to_arabic import convert_roman_to_arabic
from modules.count_roman_numerals import count_roman_numerals
from modules.article_in_bbcite import article_in_bbcite
from modules.split_page_number import split_page_number

__author__ = "Martin Bolger"
__date__ = "March 06th, 2021"

# Create the paths for the data directories
input_path, work_path, intr_path, out_path, selenium_driver_path = create_path()

data_type = "control"

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

# Filter papers with titles containing the word "Annals". These papers have no author and 
# include a date in the title that is before the cutoff date.
stacked_output = stacked_output[~stacked_output["Title"].str.contains("Annals")]

# Confirm that every time the author is "na", the observation is a duplicate.
if not stacked_output[(stacked_output["Author(s)"] == "na") & (stacked_output["dup_title"] == False) ].empty: #& ("Annals" not in stacked_output["Title"]);
    stacked_output.to_excel(out_path / "_stacked_output.xlsx", index = False)
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
stacked_output["duplicate_title_author"] = stacked_output.duplicated(subset = ["Title", "ID", "Author(s)", "Journal", "BBCite"], keep= "first")

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

# Check for articles in the BBCite field
df["Article in BBCite"] = df["BBCite"].apply(lambda x: article_in_bbcite(x))
# Swap the name of the article and BBCite if they are in the wrong field
df['Title'], df["BBCite"] = np.where(df["Article in BBCite"] == 0, [df['Title'], df["BBCite"]], [df["BBCite"], df['Title']])

# Get the BBCite year
df["BBCite Year"] = df['BBCite'].apply(lambda x: get_year(x))

# Get the first BBCite year
bbcite_year_list = df['BBCite Year'].apply(lambda x: re.search(r"\d{4}", x))
df["BBCite Year First"] = bbcite_year_list.apply(lambda x: x.group(0) if x else '')
df['BBCite Year First Mod'] = df['BBCite Year First'].replace('', "9999").astype("int")
df["Before 1963 Flag"] = df["BBCite Year First Mod"].apply(lambda x: 1 if x < 1963 else 0)

# Number of Authors
df.insert(4, 'Number of Authors', [x.count(';') + 1 for x in df['Author(s)']])

# Replace na in the type column
df['Type'] = df['Type'].str.replace('na', '')

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

# Flag volume labels that span two years
df["Vol Span Flag"] = df["Vol"].apply(lambda x: 1 if "-" in x else 0)

# Get the first number for the volumn if the volumn is a span
df["Vol First"] = df["Vol"].apply(lambda x: x.split("-")[0])
df['Vol First'] = df['Vol First'].replace('', np.nan).astype(float)

# Calculate the issue year
issue_year_list = df["Issue"].apply(lambda x: re.search(r"\d{4}", x))
df["Issue Year"] = issue_year_list.apply(lambda x: x.group(0) if x else '')

# Extract the first and last page for each paper
df["First Page"] = df["Pages"].apply(lambda x: split_page_number(x, 1))
df["Last Page"] = df["Pages"].apply(lambda x: split_page_number(x, 2))

# Count the number of Roman numeral page numbers
df["Roman Numeral Count"] = df.apply(lambda x: count_roman_numerals(x["First Page"], x["Last Page"]), axis = 1)

# Convert Roman numerals
df["First Page"] = df["First Page"].apply(lambda x: convert_roman_to_arabic(x))
df["Last Page"] = df["Last Page"].apply(lambda x: convert_roman_to_arabic(x))

# Make the type blank if it matches the BBCite or the article title
df['Type'] = df.apply(lambda x: "" if x["Type"].strip() == x["BBCite"].strip() or x["Type"].strip() == x["Title"].strip() else x["Type"], axis = 1)

# These steps drop flagged values on the dataset.

# Add the author flags using the author cut-off data
cut_off_data = pd.read_excel(
    input_path / "author_year_cut_offs_{}.xlsx".format(data_type), 
    'Sheet1'
)

# # Merge the cut-off data with the main dataset
final_output = pd.merge(
    df,
    cut_off_data,
    how = "left",
    left_on = "ID",
    right_on = "ID",
    sort = "False"
)

# Convert the types for string vars and change nan to ""
final_output["Word Exclude"] = final_output["Word Exclude"].astype(str)
final_output['Word Exclude'] = final_output['Word Exclude'].str.replace('nan', '')
final_output["BBCite Exclude"] = final_output["BBCite Exclude"].astype(str)
final_output['BBCite Exclude'] = final_output['BBCite Exclude'].str.replace('nan', '')
final_output["Journal Exclude"] = final_output["Journal Exclude"].astype(str)
final_output['Journal Exclude'] = final_output['Journal Exclude'].str.replace('nan', '')

final_output["author_exclusion_flag"] = final_output.apply(lambda x: flag_author_cut_off(x["Start Year"], x["BBCite Year First Mod"], x["Journal Exclude"], x["Journal Name"], x["Word Exclude"], x["Title"], x["BBCite Exclude"], x["BBCite"]), axis = 1)

# Subset to the rows that are not flagged by the author exclusion flag
final_output = final_output[final_output["author_exclusion_flag"] == 0]

# Subset to the rows that are not flagged by before 1963 flag
final_output = final_output[final_output["Before 1963 Flag"] == 0]

# Drop extra variables
final_output = final_output.drop(["Start Year",	"Journal Exclude", "Word Exclude", "BBCite Exclude", "author_exclusion_flag", "BBCite Year First Mod", "Before 1963 Flag", 'First Name', 'Last Name', 'Article in BBCite'], axis = 1)

# Reorder the columns
final_output = final_output[['ID', 'Title', 'Paper Type', 'Author(s)', 'Number of Authors', 'Journal', 'BBCite', 'BBCite Year', 'BBCite Year First', 'Topics', 'Subjects', "Type", 'Cited (articles)', 'Cited (cases)', 'Accessed', 'Journal Name', 'Vol', "Vol Span Flag", "Vol First", 'Issue', 'Issue Year', 'Pages', 'First Page', 'Last Page', "Roman Numeral Count"]]

# Convert numeric columns to numbers
final_output[["Number of Authors", "Cited (articles)", "Cited (cases)", "Accessed", "Vol Span Flag", "Vol First"]] = final_output[["Number of Authors", "Cited (articles)", "Cited (cases)", "Accessed", "Vol Span Flag", "Vol First"]].astype(float)

# Perform a final data check: Make sure that all IDs from the original dataset are on the output dataset
out_ids = final_output["ID"].drop_duplicates(keep='first', inplace=False).sort_values().reset_index(drop = True)

input_data = pd.read_excel(work_path / "{}.xlsx".format(data_type), 'Sheet1')

in_ids = input_data["ID"].drop_duplicates(keep='first', inplace=False).sort_values().reset_index(drop = True)

missing_ids = in_ids[~in_ids.isin(out_ids)]

if len(missing_ids) > 0:
    print("ERROR: There are ids from the original data that do not appear in the output. Ending.")
    print(missing_ids)
    quit()


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(out_path / "_stacked_paper_data_{}.xlsx".format(data_type), engine='xlsxwriter')  # pylint: disable=abstract-class-instantiated

# Convert the dataframe to an XlsxWriter Excel object.
final_output.to_excel(writer, sheet_name='Sheet1')

# Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

# Add some cell formats.
int_format = workbook.add_format({'num_format': '0'})

# Note: It isn't possible to format any cells that already have a format such
# as the index or headers or any cells that contain dates or datetimes.

# Set the column width and format for numeric columns.
# Number of Authors
worksheet.set_column('F:F', 18, int_format)
# BBCite Year First
worksheet.set_column('J:J', 18, int_format)
# Cited/Accessed Columns
worksheet.set_column('M:O', 18, int_format)
# Vol Span Flag/Vol First
worksheet.set_column('R:S', 18, int_format)
# Issue Year
worksheet.set_column('T:T', 18, int_format)
# First Page/Last Page Roman Numeral Count
worksheet.set_column('W:Y', 18, int_format)


# Close the Pandas Excel writer and output the Excel file.
writer.save()
