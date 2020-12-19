#!/usr/bin/env python
"""get_school_urls.py

This module searches for the URL of schools in a 
dataset of school URLs.

Input:
urls_df: dataframe
    This is a dataframe with school names and URLs

school_list: list
    This is a list of the schools that we are looking
    for in the main dataset.

browser_binary_path: path
    This is the path to the browser executable that Selenium
    uses to open a remote controlled browser.

selenium_driver_path: path
    This is the path to the Selenium driver for the browser.

output_path: path
    This is the path where the data will be output.

Output:
urls_df: dataframe
    This is a dataframe with the updated URL data. It is
    saved as a CSV and returned.
"""
import time
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

def get_school_urls(urls_df, school_list, browser_binary_path, selenium_driver_path, output_path):
    options = ChromeOptions()
    options.binary_location = str(browser_binary_path)
    # selenium_driver_path_string = str(selenium_driver_path)
    g_driver = webdriver.Chrome(executable_path= str(selenium_driver_path), options = options)
    url_list = []
    for school_name in school_list:
        #Remove commas from the unversity name (e.g., University of Texas, Austin becomes University of Texas Austin)
        school_name = school_name.replace(',', '')
        #This try section attempts to find the school name in the dataframe of university URLs. If it does not find it, 
        #it goes to the except section. It would be better to write a specific exception to reduce the possibility of 
        #errors
        try: 
            #This line searches for the index of the school name in the dataframe
            index = urls_df[urls_df['School Name'] == school_name].index[0]
            #This line finds the url associated with the school at that index
            url_name = urls_df['URL'][index]
            #This line prints the school name and URL
            print('found school: {} with url {}'.format(school_name, url_name))
            #The url is appended to the list of URLs
            url_list.append(url_name)
        #In the except section, the school name is serached on Google. The Selenium code find the URL on the page and saves it 
        #as the university url
        except:
            #Navigates the g_driver to Google.com
            g_driver.get("http://google.com")
            #This section is webpage manipulation. The first line finds the search box, the second line enters the school name
            #the third line presses enter
            search = g_driver.find_element_by_name('q')
            search.send_keys(school_name)
            search.send_keys(Keys.RETURN)
            #This section finds the first url that comes up on a Google search
            #find_elements_by_xpath finds specific elements on a webpages The three xpaths were found using trial and error
            #Sometimes Google includes a map or some other element before the first search result, so this handles those cases
            element = g_driver.find_elements_by_xpath('//*[@id="rso"]/div[1]/div/div[1]/div/div/div[1]/a/div/cite')
            if not element:
                element = g_driver.find_elements_by_xpath('//*[@id="rso"]/div[1]/div/div/div/div[1]/a/div/cite')
                if not element: 
                    element = g_driver.find_elements_by_xpath('//*[@id="rso"]/div[2]/div/div/div/div/div[1]/a/div/cite')
            #This section extracts the name of the url
            for elm in element:
                print(elm.text)
                url_name = elm.text
            #The url is appended to the list of URLs
            url_list.append(url_name)
            #This line prints the school name and URL
            print('Creating entry for {} with url {}'.format(school_name, url_name))
            #This line updates the URL dataframe to include an entry with the school name and URL. The next time to code
            #runs, it shouldn't have to search for the school name
            urls_df = urls_df.append(pd.DataFrame({'School Name': [school_name], 'URL': [url_name]}), ignore_index=True, sort = False)
            #This section natavigates away from Google. I did this to avoid triggering the Captcha, but it doesn't work consistantly
            #For the main code, I used Bing because Bing doesn't have a Captcha
            g_driver.get("http://amazon.com")
            time.sleep(3)
            g_driver.get("http://facebook.com")  
    #This line saves name updates to 'University and College Websites update.csv'
    urls_df.to_csv(output_path / 'university_and_college_websites.csv', index=False)
    return urls_df