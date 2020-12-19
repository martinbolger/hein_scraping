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

from modules.create_path import create_path
from modules.hein_scraping_functions import webpage_wait, get_paper_data, mod_names, check_google, similar_names, search_names
from modules.data_manipulation_functions import to_float_or_int, create_dataframe_dict, remove_commas, check_files, check_df

stats = ['Cited by Cases','Cited by Articles','Accessed (Past 12 Months)','Cited by Articles (Past 10 Years)', 'Cited by Articles (Past 1-2 years)', 'ScholarCheck Rank', 'Average Citations per Article', 'Average Citations per Document', 'Self-Citations']
#This is the path to the directory where the individual CSVs will be stored
path = create_path('multi_school_data', 'multi_school_data')
#This gives the files that are currently in the directory
files = os.listdir(path)
print(files)
#If we were scraping a specific school, it would be named here
school_name = 'multi_school'

#This is how long the webdriver will wait while loading pages
delay = 5

#This is a dataframe of names that we want to manually change 
#This can be used if we found errors in the data (for example, names were not scraped)
name_mod = pd.read_csv('Professor_Names_name_mod.csv')


#These three lines give a list of the files that have already been scraped
#Papers gives a list of the papers by each author
#Stats gives the stat table at the top of each author's page
#Skip gives a list of the skipped names

current_papers = os.listdir(create_path('author_papers', 'multi school data'))
current_stats = os.listdir(create_path('school_stats'))
current_skip = os.listdir(create_path('skipped_names'))
#The file should be the list of names. If there are multiple schools, the files are the individual files for each school
for file in files:
    print(file)
    #This creates that main stat dataframe that will be modified
    main_df = pd.DataFrame()
    #This funciton checks if a stat CSV for the school has already been created. 
    file1 = check_df(current_stats, school_name)
    #If a stat CSV for the school has been created, it is loaded. This is useful if the program stopped before it finished
    #going through the full name list
    if file1 != '':
        main_df = pd.read_csv(create_path('school_stats', file1))
    #This creates the main skipped name dataframe that will be modified
    skip_df = pd.DataFrame(columns = ['Full Name', 'School'])
    #This function checks if a skipped name dataframe has already been created
    file2 = check_df(current_skip, school_name)
    #If a stat CSV for the school has been created, it is loaded. This is useful if the program stopped before it finishe 
    #going through the full name list
    if file2 != '':
        skip_df = pd.read_csv(create_path('skipped_names', file2))
    #This step reads the main data (this is the list of names of professors)
    data = pd.read_csv(os.path.join(path, file)) 
    #This loop goes through each name
    for i in range(len(data)):
        #This section gets the professor's information from the dataframe 
        #ID
        prof_id = data['ID'][i]
        #First Name and middle name
        mid_first_name = data['First Name'][i]
        #Last Name
        last_name = data['Last Name'][i]
        #Full Name
        full_name = mid_first_name + ' ' +  last_name
        #This line gets the school URLs from the dataframe
        school_url = [data['School URL short'][i], data['New School URL short'][i]]
        #Checks if a file for the papers from the professor has already been created
        done = check_files(mid_first_name, last_name, current_papers)
        #If a file has already been created for the professor, the loop moves onto the next name
        if done:
            print('File for ' + full_name + ' has already been created.')
            continue
        #School name
        school = data['School'][i]
        #New school name
        new_school = data['New School'][i]
        #Title 
        title = data['Title'][i]
        page_name = []
        err_fm_names = []
        df_sub = pd.DataFrame()
        print(mid_first_name)
        print(last_name)
        
        #Search by author to find potential alternative first and middle names:
        fm_names, err_fm_names = search_names(mid_first_name, last_name, school_url)
        #This function manually changes names using the name_mod dataframe
        fm_names = mod_names(fm_names, err_fm_names, name_mod)

        #If there were no matching names, the name is added to the skipped names list and the loop moves onto the next name
        if not fm_names:
            print('Name ' + full_name + ' was not found')
            skip_df = skip_df.append(pd.DataFrame([[full_name, school, new_school, title]], columns = ['Full Name', 'School', 'New School', 'Title']), sort=False)
            
        #This section loops through the list of alternative names and goes directly to their pages on Hein
        for fm_name in fm_names:
            #Link to Heil page
            link = 'https://heinonline-org.proxy01.its.virginia.edu/HOL/AuthorProfile?action=edit&search_name=' + last_name +  '%2C ' + fm_name + '&collection=journals'
            #Direct the webdriver to the page
            driver.get(link)
            #This function waits for the webpage to load
            webpage_wait('//*[@id="page_content"]/div[1]/div/div[1]/div[1]')
            #This gets the page HTML
            soup=bs.BeautifulSoup(driver.page_source, 'lxml')
            #This find the stat table at the top of the page
            table_rows = soup.findAll('td', {'style': 'text-align:right;'})
            #This gives the full name
            full_name = fm_name + ' ' +  last_name
            #This function checks the similar names list on the Hein page to append additional names
            fm_names, err_fm_names = similar_names(fm_names, err_fm_names, fm_name, last_name)
            #This function checks the name_mod CSV again
            fm_names = mod_names(fm_names, err_fm_names, name_mod)
            
            
            cur_page = driver.find_element_by_xpath('//*[@id="page_content"]/div[1]/div/div[1]/div[1]').text
            if not table_rows:
                got_page = False
                new_names = False
                link_index = 1
                while new_names == False:
                    try:
                        if link_index == 1:
                            element =driver.find_element_by_xpath('//*[@id="page_content"]/div[2]/div/ul/li/a')
                        else: 
                            element =driver.find_element_by_xpath('//*[@id="page_content"]/div[2]/div/ul/li[' + str(link_index) + ']/a')            
                        new_fm_name = element.text.split(', ')[1]
                        new_last_name = element.text.split(', ')[0]
                        if last_name == new_last_name and mid_first_name in new_fm_name:
                            if not new_fm_name in fm_names:
                                check_google(new_fm_name, last_name, school_url)
                                fm_names.append(new_fm_name)
                            
                    except: 
                        new_names = True
                        got_page = True
                        if not scraped_papers:
                            print('Name ' + full_name + ' is not in the database. You may be missing a middle initial.')
                            skip_df = skip_df.append(pd.DataFrame([[full_name, school, title]], columns = ['Full Name', 'School', 'Title']), sort=False)
                        else:
                            print('No remaining pages to scrape for {}.'.format(full_name))
                    link_index += 1
            #If there is a table on the page
            elif table_rows and cur_page not in page_name: 
                element = driver.find_element_by_xpath('//*[@id="page_content"]/div[1]/div/div[2]')
                table_element = element.text.split('\n')
                #If the table is empty, there is no data to scrape
                if len(table_element) < 5:
                    print('No data available on Hein for {} {}'.format(fm_name, last_name))
                #If the table is full, this section rearranges the data into a better format
                else:                    
                    #This section scrapes the paper data. The index values are based on the way the xpaths are incremented
                    #The scroll number tracks the number of times the page has scrolled. This is for pages with a large number of 
                    #papers. The xpaths change when the page scrolls.
                    title_index = 3
                    stats_index = 4
                    topic_index = 0
                    scroll_num = 0
                    #This gets the page source
                    soup=bs.BeautifulSoup(driver.page_source, 'lxml')
                    #This section gets the paper topics
                    topic_array = soup.findAll('div', {'class': 'topics'})
                    element = title_index
                    page_name = []
                    df = pd.DataFrame(columns = ['Title', 'Author(s)', 'ID', 'Journal', 'BBCite', 'Topics', 'Cited (articles)', 'Cited (cases)', 'Accessed'])
                    #This while loop will continue until there are no more papers on the page
                    while element:
                        #Data stream is a list of the data in the paper data box (for example, authors, topics, journal)
                        data_stream = []
                        #This funciton returns a dictionary with various fields for each variable in the data box
                        #Sometimes some of the variables are missing (for example, there are papers without a journal listed)
                        #In this case, the dictionary returns an empty value for these variables
                        data_dict = get_paper_data(last_name, prof_id, title_index, scroll_num)
                        #This section gets the paper stats box. This is the box that says how many citations the paper
                        #has received
                        if scroll_num == 0:
                            element = driver.find_elements_by_xpath('//*[@id="save_results"]/div/div/div/div[' + str(stats_index) + ']/div[2]/div')
                        elif scroll_num > 0:
                            element = driver.find_elements_by_xpath('//*[@id="save_results"]/div[' + str(stats_index) + ']/div[2]/div')
                        #This section extracts the data from the paper stats box
                        for elm in element:
                            cited_text = elm.text
                        article_citations = 'na'
                        case_citations = 'na'
                        accessed = 'na'
                        if not isinstance(cited_text, list):
                            cited_text = cited_text.split('\n')
                            #This section finds the value for each paper stat
                            for stat in cited_text:
                                if 'Article' in stat:
                                    article_citations = int(re.search(r'\d+', stat).group())
                                if 'Case' in stat:
                                    case_citations = int(re.search(r'\d+', stat).group())
                                if 'Accessed' in stat:
                                    accessed = int(re.search(r'\d+', stat).group())
                        #The values are appended to the data_stream list
                        data_stream.append(article_citations)
                        data_stream.append(case_citations)
                        data_stream.append(accessed)
                        #This line adds the output from the function get_paper_data to the data_stream list
                        data_stream = list(data_dict.values()) + data_stream
                        #The data_stream list is used to add a line of data to the overall paper dataframe for this author
                        df = df.append(pd.DataFrame([data_stream], columns = ['Title', 'Author(s)', 'ID', 'Journal', 'BBCite', 'Topics', 'Cited (articles)', 'Cited (cases)', 'Accessed']), sort=False)
                        #The indices are augmented to get the next paper
                        stats_index +=4
                        title_index += 4
                        page_name.append(cur_page)
                        #Check that next paper exists:
                        if scroll_num == 0:
                            x_path_title = '//*[@id="save_results"]/div/div/div/div[' + str(title_index) + ']/div[2]/dt[1]/div'
                        #If the page has scrolled, the xpath we need to check has changed
                        if scroll_num > 0:
                            x_path_title = '//*[@id="save_results"]/div[' + str(title_index) + ']/div[2]/dt[1]/div'
                        element = driver.find_elements_by_xpath(x_path_title)
                        #If we can't find a next paper, it could be because we need to scroll again
                        #This section attempts to scroll the page. 
                        if not element:
                            scroll_num +=1
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            box_element = driver.find_elements_by_xpath('//*[@id="results_total"]')
                            num_papers = int(box_element[0].text.split(' ')[0])
                            #If there are more than 100 papers, we know there are still paper left to scrape
                            if num_papers > 100*scroll_num:
                                time.sleep(15)
                                title_index = 3
                                stats_index = 4
                                topic_index = 0
                                x_path_title = '//*[@id="save_results"]/div[' + str(title_index) + ']/div[2]/dt[1]/div'
                                element = driver.find_elements_by_xpath(x_path_title)
                    #This line saves the CSV of papers
                    df.to_csv(create_path('author_papers', 'multi school data', '{}_{}_{}_papers.csv'.format(full_name, prof_id, school)),index=False)
                    time.sleep(3)
                #If we reach this point, all the pages for that author have been scraped
                print('No remaining pages to scrape for {}.'.format(fm_name + ' ' + last_name))  
        #If there are elements in the sub stat dataframe, they need to be added to the main stat dataframe
        if not df_sub.empty:
            my_dict = {'Person': [full_name], 'ID': [prof_id], 'School': [school], 'Type': ['number']}
            name_data = pd.DataFrame(my_dict)
            df_sub = pd.concat([name_data, df_sub], sort = False, axis = 1)
            main_df = pd.concat([main_df, df_sub], sort = False)
            main_df.replace(0, 'na')
            main_df.to_csv(create_path('school_stats', '{}_stats.csv'.format(school_name)),index=False)                
#         skip_df.to_csv(create_path('skipped_names', '{}_skipped.csv'.format(school_name)), index = False)

#These lines save the final version of the stat and skipped names CSVs. We only want to save the skipped names at the 
#end becuase we want the code to consider those names if we rerun it. 
skip_df.to_csv(create_path('skipped_names', '{}_skipped.csv'.format(school_name)),index=False)
main_df.replace(0, 'na')
main_df.to_csv(create_path('school_stats', '{}_stats.csv'.format(school_name)),index=False)