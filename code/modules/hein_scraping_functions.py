from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import bs4 as bs
import os
import numpy as np
import re
import time
import nltk
import requests
import random
import math

from modules.data_manipulation_functions import list_to_comma_separated_string

# from data_manipulation_functions import list_to_comma_separated_string

# This function creates a remote control browser
def create_browser(browser_binary_path, selenium_driver_path):
    options = ChromeOptions()
    options.binary_location = str(browser_binary_path)
    # selenium_driver_path_string = str(selenium_driver_path)
    driver = webdriver.Chrome(executable_path= str(selenium_driver_path), options = options)
    return driver

#This function searches for a string of text using the advanced search function in Hein
# It is used to find the number of hits for different book titles after a certain year.
def search_hein_for_books(search_text, year, driver):
    
    # Go to the main page
    link = 'https://heinonline-org.proxy01.its.virginia.edu/HOL/LuceneSearch?collection=all&searchtype=open'
    driver.get(link)

    # Wait for the page logo to load
    webpage_wait('//*[@id="heinlogo"]/a/img', driver)

    # Enter the search text
    full_text = driver.find_element_by_xpath('//*[@id="termsc"]') 
    full_text.send_keys(search_text)

    # Enter the year cutoff
    year_text = driver.find_element_by_xpath('//*[@id="yearlo"]') 
    year_text.send_keys(year)

    # Click the search button
    search = driver.find_element_by_xpath('//*[@id="full_text_advanced_search_box"]/div[3]/div/button[1]').click()
    try:
        # Look for the number of results pannel
        results_count_elm = driver.find_element_by_xpath('//*[@id="results_total"]')
        results_count_text = results_count_elm.text
        # This only matches integers up to 999,999, but I doubt that will be a problem.
        match = re.search(r"^(0|[1-9]\d{0,2},?\d*) results", results_count_text)
        result_count = match.group(1)
    except NoSuchElementException:
        # If the results pannel element wasn't found, there were no results.
        result_count = 0
    
    return result_count


#This function searches for a professor's name on Hein. It goes through the papers that show up and checks for authors
#with the same first and last name. Once a match is found, the name is searched on Bing using the function check_bing
#If the correct school name shows up on the Bing search, the name is added to the alternative name list (alt_fm_names.
#Otherwise, the name is added to the error list (err_fm_names)
def search_names(mid_first_name, last_name, school_url, driver, g_driver, s_driver):
    link = 'https://heinonline-org.proxy01.its.virginia.edu/HOL/LuceneSearch?typea=title&termsa=&operator=AND&typeb=creator&termsb=' + last_name + '+' + mid_first_name + '&operatorb=AND&typec=text&termsc=&operatorc=AND&typed=title&termsd=&operatord=AND&typee=title&termse=&operatore=AND&typef=title&termsf=&yearlo=&yearhi=&tabfrom=&searchtype=field&collection=all&submit=Go'
    driver.get(link)
    try:
        webpage_wait('//*[@id="heinlogo"]/a/img', driver)
        driver.find_element_by_xpath('//*[@id="search_modify"]/form/div/div/div/div/a[4]/i').click()
    except:
        driver.find_element_by_xpath('//*[@id="search_modify"]/div')
    element = driver.find_elements_by_tag_name('a')
    alt_fm_names = []
    err_fm_names = []
    middle_name_found = 0
    if ' ' in mid_first_name.lower():
        first_name = mid_first_name.split(' ')[0]
    else: 
        first_name = mid_first_name
    page = 1
    while element:
        for link in element:
            link_text = link.text.lower()
            # Make sure punctuation is matched literally
            escaped_first_name = re.escape(first_name.lower())
            escaped_last_name = re.escape(last_name.lower())
            # Search for the first and last name in the link text. We want to see them in the expected position
            if bool(re.search(r", {}(\s|$)".format(escaped_first_name), link_text.lower(), flags = re.I)) and bool(re.search(r"(^|; ){}, ".format(escaped_last_name), link_text.lower(), flags = re.I)) and '[' not in link_text:
                new_last = link_text.split(', ')[0]
                new_first_mid = link_text.split(', ')[1]
                if first_name.lower() in new_first_mid and last_name.lower() == new_last:
                    new_fm = link.text.split(', ')[1]
                    if not new_fm in alt_fm_names and not new_fm in err_fm_names:
                        print(new_fm + ' ' + last_name)
                        faculty = check_bing(new_fm, last_name, school_url, g_driver)
                        if faculty: 
                            alt_fm_names.append(new_fm)
                        else: 
                            err_fm_names.append(new_fm)
                        # Flag if a middle name was found
                        if ' ' in new_fm:
                            middle_name_found = 1
                        # If a middle name has not been found, we can check the similar names
                        if middle_name_found == 0:
                            link = 'https://heinonline-org.proxy01.its.virginia.edu/HOL/AuthorProfile?action=edit&search_name=' + last_name +  '%2C ' + new_fm + '&collection=journals'
                            s_driver.get(link)
                            similar_names = get_similar_names(first_name, last_name, s_driver)
                            alt_fm_names, err_fm_names = check_similar_names(alt_fm_names, err_fm_names, similar_names, school_url, g_driver)    

        if page < 2:
            try:
                driver.find_element_by_xpath('//*[@id="thenext"]/span').click()
                time.sleep(3)
                element = driver.find_elements_by_tag_name('a') 
                page += 1
            except:
                element = []
        else: 
            element = []
    # Convert the output to a string format
    alt_fm_names_str  = list_to_comma_separated_string(alt_fm_names)
    err_fm_names_str  = list_to_comma_separated_string(err_fm_names)
    return alt_fm_names_str, err_fm_names_str

def get_similar_names(first_name, last_name, s_driver):
    # Wait for the page to load
    webpage_wait('//*[@id="heinlogo"]/a/img', s_driver)
    # Check for the similar pages link
    links = s_driver.find_elements_by_tag_name('a')
    for link in links:
        if link.text == "Similar Author Names":
            link.click()
    # Read the similar names list
    try:
        element = s_driver.find_element_by_xpath('//*[@id="similar-authors"]/div/ul')
    except NoSuchElementException:
        return []
    similar_name_list = [a.strip() for a in element.text.split('\n')]
    output_similar_name_list = []
    # Make sure punctuation is matched literally
    escaped_first_name = re.escape(first_name.lower())
    escaped_last_name = re.escape(last_name.lower())
    for similar_name in similar_name_list:
        if bool(re.search(r", {}(\s|$)".format(escaped_first_name), similar_name.lower(), flags = re.I)) and bool(re.search(r"(^|; ){}, ".format(escaped_last_name), similar_name.lower(), flags = re.I)) and ', ' in similar_name.lower():
            output_similar_name_list.append(similar_name)
    return output_similar_name_list

def check_similar_names(alt_name_list, err_fm_names, similar_name_list, school_url, g_driver):
    for name in similar_name_list:
        if '*' in name:
            name = name.split('*')[1]
        elif '#' in name:
            name = name.split('#')[1]
        new_fm = name.split(', ', 1)[1]
        new_last = name.split(', ', 1)[0]
        if new_fm not in alt_name_list and not new_fm in err_fm_names:
            print(new_fm + ' ' + new_last)
            faculty = check_bing(new_fm, new_last, school_url, g_driver)
            if faculty: 
                alt_name_list.append(new_fm)
            else: 
                err_fm_names.append(new_fm)
    return alt_name_list, err_fm_names

#This function searches for a name on Bing and checks if any of the results that come up contain the school URL.
#When there is no middle initial or middle name, the school url is included in the search. Otherwise, only the name is 
#searched. I found that this method works well because when there is no middle name, there is sometimes a more famous
#person with the same name
def check_bing(mid_first_name, last_name, school_url, g_driver):
    faculty = False
    for url in school_url:
        if faculty == True:
            break
        g_driver.get("http://bing.com")
        search = g_driver.find_element_by_xpath('//*[@id="sb_form_q"]')
        if not ' ' in mid_first_name:
            search.send_keys(mid_first_name + ' ' + last_name + ' ' + url.split(".")[0])
        else: 
            search.send_keys(mid_first_name + ' ' + last_name + ' ')
        search.send_keys(Keys.RETURN)
        # Wait until the page has loaded to scrape the links
        webpage_wait('//*[@id="sb_privacy"]', g_driver)
        elems = g_driver.find_elements_by_xpath("//a[@href]")

        print("URL: {}".format(url))
        for elem in elems:
            try:
                if url in elem.get_attribute("href"):
                    print(url + ' in: ' + elem.get_attribute("href"))
                    faculty = True
                    break
            except StaleElementReferenceException:
                print("Stale element")
                continue

        g_driver.get("http://amazon.com")
        time.sleep(3)
        g_driver.get("http://facebook.com")
    return faculty

#This function changes the list of names manually
def mod_names(fm_names, err_fm_names, name_mod):
    if not name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['fm_names'].empty or not name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['err_fm_names'].empty:
        print('passed')
        if [x for x in list(name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['fm_names']) if str(x) != 'nan']:
            print('passed 1')
            for name in name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['fm_names'].values[0].split(','):
                if name not in fm_names:
                    fm_names = fm_names + [name]
                print(fm_names)
        if [x for x in list(name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['err_fm_names']) if str(x) != 'nan']:
            print('passed 2')
            try:
                fm_names.remove(list(name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['err_fm_names'])[0])
            except:
                print('Name {} was not in the list'.format(name_mod.query('@mid_first_name == first_mid_name and @last_name == last_name')['err_fm_names'].values[0].split(',')))
    print(fm_names)
    return fm_names

#This function gets all the paper data and appends it to the list data_stream
def get_paper_data(last_name, prof_id, title_index, scroll_num, driver):
    data_stream = []
    data_stream = dict.fromkeys(['Title','Author', 'id', 'Journal', 'BBCite', 'Topics', 'Subjects', 'Type'], 'na')
    data_stream['id'] = prof_id
    # Make sure that the page has loaded the first papers
    webpage_wait('//*[@id="sortby"]', driver)
    if scroll_num == 0:
        element = driver.find_elements_by_xpath('//*[@id="save_results"]/div/div/div/div[' + str(title_index) + ']/div[2]')      
    elif scroll_num > 0:
        element = driver.find_elements_by_xpath('//*[@id="save_results"]/div[' + str(title_index) + ']/div[2]')
    for elm in element:
        my_list = elm.text
    # Remove strings that say "More Information" or "Full Text Not Currently Available in HeinOnline"
    my_list_clean = re.sub(r'\nMore Information\n|Full Text Not Currently Available in HeinOnline|\* Search your library catalog|Publisher link to article', ' ', my_list)
    # Create a list of strings with the data
    data_list = my_list_clean.split('\n')
    # Strip the strings in the list
    data_list = list(map(str.strip, data_list))
    # Remove blank strings from the list
    data_list = list(filter(None, data_list))
    data_stream['Title'] = data_list[0]
    # See if the second line matches one of our other fields. If it does not, make it a type field
    substrings = ['Topics: ', 'Subjects: ', 'Vol.', last_name]
    if not any([substring in data_list[1] for substring in substrings]):
        data_stream['Type'] = data_list[1]
    for a in data_list[1:]:
        if 'Topics: ' in a:
            data_stream['Topics'] = a.split('Topics: ')[1]
        elif 'Subjects: ' in a:
            data_stream['Subjects'] = a.split('Subjects: ')[1]
        elif 'Vol.' in a:
            data_stream['Journal'] = a
        elif last_name + "," in a:
            data_stream['Author'] = a
        else:
            data_stream['BBCite'] = a
    return data_stream

#This function waits for the webpage to load by waiting until a webpage element appears
def webpage_wait(xpath, driver):
    element = []
    while not element:
        try:
            element = driver.find_element_by_xpath(xpath)
        except:
            print('Page has not loaded, sleeping for 3 seconds')
            time.sleep(3)