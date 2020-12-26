from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
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

# This function creates a remote control browser
def create_browser(browser_binary_path, selenium_driver_path):
    options = ChromeOptions()
    options.binary_location = str(browser_binary_path)
    # selenium_driver_path_string = str(selenium_driver_path)
    driver = webdriver.Chrome(executable_path= str(selenium_driver_path), options = options)
    return driver

#This function searches for a professor's name on Hein. It goes through the papers that show up and checks for authors
#with the same first and last name. Once a match is found, the name is searched on Bing using the function check_google
#If the correct school name shows up on the Bing search, the name is added to the alternative name list (alt_fm_names.
#Otherwise, the name is added to the error list (err_fm_names)
def search_names(mid_first_name, last_name, school_url, driver, g_driver):
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
    if ' ' in mid_first_name.lower():
        first_name = mid_first_name.split(' ')[0]
    else: 
        first_name = mid_first_name
    page = 1
    while element:
        for link in element:
            link_text = link.text.lower()
            if first_name.lower() in link_text.lower() and last_name.lower() in link_text.lower() and '[' not in link_text:
                try:
                    new_last = link_text.split(', ')[0]
                    new_first_mid = link_text.split(', ')[1]
                    if first_name.lower() in new_first_mid and last_name.lower() == new_last:
                        new_fm = link.text.split(', ')[1]
                        if not new_fm in alt_fm_names and not new_fm in err_fm_names:
                            faculty = check_google(new_fm, last_name, school_url, g_driver)
                            if faculty: 
                                alt_fm_names.append(new_fm)
                            else: 
                                err_fm_names.append(new_fm)
                except:
                    continue
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

#This function checks if any of the names in the similar names list of the Hein page are the relevant author
def similar_names(alt_name_list, err_fm_names, mid_first_name, last_name, school_url, driver, g_driver):
    try:
        driver.find_element_by_xpath('//*[@id="page_content"]/div[2]/div/b/a').click()
        element = driver.find_element_by_xpath('//*[@id="simlist"]/ul[1]')
        similar_name_list = [a.strip() for a in element.text.split('\n')]
        middle_name = ''
        if ' ' in mid_first_name.lower():
            first_name = mid_first_name.split(' ')[0]
            middle_name = mid_first_name.split(' ')[1]
        else: 
            first_name = mid_first_name
        for name in similar_name_list:
            if '*' in name:
                name = name.split('*')[1]
            elif '#' in name:
                name = name.split('#')[1]
            if first_name.lower() in name.lower() and last_name.lower() in name.lower() and ', ' in name.lower():
                new_fm = name.split(', ', 1)[1]            
                new_last = name.split(', ', 1)[0]
                print(new_fm + ' ' + new_last)
                if new_fm not in alt_name_list and last_name.lower() == new_last.lower() and not new_fm in err_fm_names:
                    if ' ' in new_fm.lower() and middle_name != '':
                        new_mi = new_fm.split(' ')[1][0].lower()
                        if new_mi == middle_name[0].lower():
                            alt_name_list.append(new_fm)
                            continue
                    faculty = check_google(new_fm, last_name, school_url, g_driver)
                    if faculty: 
                        alt_name_list.append(new_fm)
                    else: 
                        err_fm_names.append(new_fm)
    except:
        print('No similar names found.')
    return alt_name_list, err_fm_names

#This function searches for a name on Bing and checks if any of the results that come up contain the school URL.
#When there is no middle initial or middle name, the school url is included in the search. Otherwise, only the name is 
#searched. I found that this method works well because when there is no middle name, there is sometimes a more famous
#person with the same name
def check_google(mid_first_name, last_name, school_url, g_driver):
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
           if url in elem.get_attribute("href"):
                print(url + ' in: ' + elem.get_attribute("href"))
                faculty = True
                break

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
    data_stream = dict.fromkeys(['Title','Author', 'id', 'Journal', 'BBCite', 'Topics'], 'na')
    data_stream['id'] = prof_id
    if scroll_num == 0:
        element = driver.find_elements_by_xpath('//*[@id="save_results"]/div/div/div/div[' + str(title_index) + ']/div[2]')      
    elif scroll_num > 0:
        element = driver.find_elements_by_xpath('//*[@id="save_results"]/div[' + str(title_index) + ']/div[2]')
    for elm in element:
        my_list = elm.text
    data_list = my_list.split('\n')
    data_stream['Title'] = data_list[0]
    for a in data_list[1:]:
        if not 'More Information' in a and not a == '':
            if 'Topics: ' in a:
                data_stream['Topics'] = a.split('Topics: ')[1]
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