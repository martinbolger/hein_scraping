from selenium import webdriver
import pandas as pd
import bs4 as bs
import os
import numpy as np
import re
import time
from selenium.webdriver.common.keys import Keys
import nltk

driver = webdriver.Chrome()
driver.get("http://proxy.its.virginia.edu/login?url=http://heinonline.org/HOL/Welcome")
g_driver = webdriver.Chrome()
g_driver.get("http://google.com")

username = 'meb2fv'
password = '0ver In 2018!'
driver.find_element_by_id("user").send_keys(username);
driver.find_element_by_id("pass").send_keys(password);
driver.find_element_by_xpath("/html/body/main/div[2]/fieldset/form/input").click()

def search_names(mid_first_name, last_name, school_url):
    link = 'https://heinonline-org.proxy01.its.virginia.edu/HOL/LuceneSearch?typea=title&termsa=&operator=AND&typeb=creator&termsb=' + last_name + '+' + mid_first_name + '&operatorb=AND&typec=text&termsc=&operatorc=AND&typed=title&termsd=&operatord=AND&typee=title&termse=&operatore=AND&typef=title&termsf=&yearlo=&yearhi=&tabfrom=&searchtype=field&collection=all&submit=Go'
    driver.get(link)
    try:
        driver.find_element_by_xpath('//*[@id="search_modify"]/form/div/div/div/div/a[4]/i').click()
    except:
        driver.find_element_by_xpath('//*[@id="search_modify"]/div')
    element = driver.find_elements_by_tag_name('a')
    full_name = mid_first_name + ' ' +  last_name
    alt_fm_names = []
    err_fm_names = []
    if ' ' in mid_first_name.lower():
        first_name = mid_first_name.split(' ')[0]
    else: 
        first_name = mid_first_name
#     print(mid_first_name.lower())
#     print(last_name.lower())
    page = 1
    
    while element:
        for link in element:
            link_text = link.text.lower()
            if mid_first_name.lower() in link_text.lower() and last_name.lower() in link_text.lower() and '[' not in link_text:
                try:
                    new_last = link_text.split(', ')[0]
                    new_first_mid = link_text.split(', ')[1]
                    if mid_first_name.lower() in new_first_mid and last_name.lower() in new_last:
#                         print(link_text)
                        new_fm = link.text.split(', ')[1]
                        if not new_fm in alt_fm_names and not new_fm in err_fm_names:
                            faculty = check_google(new_fm, last_name, school_url)
                            if faculty: 
                                alt_fm_names.append(new_fm)
#                                 print(new_fm)
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
                print('0k')
            except:
                element = []
        else: 
            element = []
    return alt_fm_names

    def check_google(mid_first_name, last_name, school_url):
    faculty = False
    g_driver.get("http://google.com")
    search = g_driver.find_element_by_name('q')
    if not '.' in mid_first_name:
        search.send_keys(mid_first_name + ' ' + last_name + ' ' + school_url)
    else: 
        search.send_keys(mid_first_name + ' ' + last_name + ' ')
    search.send_keys(Keys.RETURN)
    elems = g_driver.find_elements_by_xpath("//a[@href]")
    
    for elem in elems:
        if school_url in elem.text:
            print(school_url + ' in: ' + elem.text)
            faculty = True
            break
    return faculty

    def create_path(*args):
    cur_path = os.getcwd()
    for value in args:
        cur_path  = os.path.join(cur_path, value)
    return cur_path

def to_float_or_int(input_list):
    new_list = []
    for x in input_list:
        x = x.replace(',','')
        try:
            value = int(x)
        except ValueError:
            try:
                value = float(x)
            except:
                value = ''
        new_list.append(value)
    return new_list

def create_dataframe_dict(my_list):#, person, school, data_type):
#     my_dict = {'Person': person, 
#               'School': school, 
#               'Type': data_type}
    my_dict = {}
    for stat in stats:
        my_dict[stat] = ''
        for item in my_list:   
            if item[0] == stat:
                my_dict[stat] = item[1]  
    return my_dict

def remove_commas(df1):
    for col in df1.columns:
        df1[col] = df1[col].str.replace(',', '')
    return df1

    os.getcwd()
stats = ['Cited by Cases','Cited by Articles','Accessed (Past 12 Months)','Cited by Articles (Past 10 Years)', 'Cited by Articles (Past 1-2 years)', 'ScholarCheck Rank', 'Average Citations per Article', 'Average Citations per Document', 'Self-Citations']
path = os.path.join(os.getcwd(), 'school_data')
files = os.listdir(path)
school_url = 'asu'
for file in files[0:1]:
    print(file)
    main_df = pd.DataFrame()
    skip_df = pd.DataFrame(columns = ['Full Name', 'School'])
    data = pd.read_csv(os.path.join(os.getcwd(), 'school_data', file))   
    for i in range(len(data)):
        #Get name and information from the database
        mid_first_name = data['First Name'][i]
        last_name = data['Last Name'][i]
        full_name = mid_first_name + ' ' +  last_name
        school = data['School'][i]
        title = data['Title'][i]
        page_name = []
        df_sub = pd.DataFrame()
        #Search by author to find potential alternative first and middle names:
        fm_names = search_names(mid_first_name, last_name, school_url)
        if not fm_names:
            print('Name ' + full_name + ' was not found')
            skip_df = skip_df.append(pd.DataFrame([[full_name, school, title]], columns = ['Full Name', 'School', 'Title']))
            
        for fm_name in fm_names:
            link = 'https://heinonline-org.proxy01.its.virginia.edu/HOL/AuthorProfile?action=edit&search_name=' + last_name +  '%2C ' + fm_name + '&collection=journals'
            driver.get(link)
            soup=bs.BeautifulSoup(driver.page_source, 'lxml')
            table_rows = soup.findAll('td', {'style': 'text-align:right;'})
            full_name = fm_name + ' ' +  last_name
            cur_page = driver.find_element_by_xpath('//*[@id="page_content"]/div[1]/div/div[1]/div[1]').text
            if str(table_rows[1]) == '<td style="text-align:right;"> 1 </td>':
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
                            skip_df = skip_df.append(pd.DataFrame([[full_name, school, title]], columns = ['Full Name', 'School', 'Title']))
                        else:
                            print('No remaining pages to scrape from {}.'.format(full_name))
                    link_index += 1
                    
            elif str(table_rows[1]) != '<td style="text-align:right;"> 1 </td>' and cur_page not in page_name: 
                element = driver.find_element_by_xpath('//*[@id="page_content"]/div[1]/div/div[2]/div[1]')
                table_element = element.text.split('\n')
                number_list = []
                rank_list = []
                stat_list = []
                for stat in stats:
                    find_index = [table_element.index(s) for s in table_element if stat == s]
                    if find_index:
                        my_list = table_element[find_index[0]+1].split(' ')
                        number_list.append(my_list[0])
                        stat_list.append(stat)
                        if len(my_list) > 1:
                            rank_list.append(my_list[-1])
                    if stat == 'Self-Citations':
                        find_index = [table_element.index(s) for s in table_element if stat in s]
                        if find_index:
                            stat_list.append(stat)
                            number_list.append(table_element[find_index[0]].split(' ')[1])
                zip_number_list = list(zip(stat_list, number_list))
                zip_rank_list = list(zip(stat_list, rank_list))
                number_dict = create_dataframe_dict(zip_number_list)
                rank_dict = create_dataframe_dict(zip_rank_list)
                df_number = pd.DataFrame.from_dict(number_dict, orient='index').transpose()
                df_rank = pd.DataFrame.from_dict(rank_dict, orient='index').transpose()
                df_number = df_number.replace('na', '0')
                df_number = df_number.replace('', '0')
                df_number = df_number.replace(' ', '0')
                df_number = remove_commas(df_number)
                df_number = df_number.astype(float)
                if df_sub.empty:
                    df_sub = df_number
                else: 
                    df_sub = df_sub.add(df_number)
                
                title_index = 3
                stats_index = 4
                topic_index = 0
                topic_div_index = 0
                topic_array = soup.findAll('div', {'class': 'topics'})
                element = title_index
                df = pd.DataFrame(columns = ['Title', 'Author(s)', 'Journal', 'Cited (articles)', 'Cited (cases)', 'Accessed', 'Topics'])
                while element:
                    data_stream = []
                    x_path_title = '//*[@id="save_results"]/div/div/div/div[' + str(title_index) + ']/div[2]/dt[1]/div'
                    element = driver.find_elements_by_xpath(x_path_title)
                    #Get title:
                    if element:
                        scraped_papers = True
                        for elm in element:
                            data_stream.append(elm.text)

                        element = driver.find_elements_by_xpath('//*[@id="save_results"]/div/div/div/div[' + str(title_index) + ']/div[2]')
                        for elm in element:
                            my_list = elm.text
                        if [a for a in my_list.split('\n') if last_name in a]:   
                            data_stream.append([a for a in my_list.split('\n') if last_name in a][0])
                        else:
                            data_stream.append('na')
                        if [a for a in my_list.split('\n') if 'Vol.' in a]:
                            data_stream.append([a for a in my_list.split('\n') if 'Vol.' in a][0])
                        else:
                            data_stream.append('na')
                        element = driver.find_elements_by_xpath('//*[@id="save_results"]/div/div/div/div[' + str(stats_index) + ']/div[2]/div')
                        for elm in element:
                            cited_text = elm.text
                        article_citations = 'na'
                        case_citations = 'na'
                        accessed = 'na'
                        if not isinstance(cited_text, list):
                            cited_text = cited_text.split('\n')
                            cited_text
                            for stat in cited_text:
                                if 'Article' in stat:
                                    article_citations = int(re.search(r'\d+', stat).group())
                                if 'Case' in stat:
                                    case_citations = int(re.search(r'\d+', stat).group())
                                if 'Accessed' in stat:
                                    accessed = int(re.search(r'\d+', stat).group())
                        data_stream.append(article_citations)
                        data_stream.append(case_citations)
                        data_stream.append(accessed)
                        try:
                            data_stream.append(topic_array[topic_div_index].text.split(':')[1])
                        except:
                            data_stream.append('na')
                        df = df.append(pd.DataFrame([data_stream], columns = ['Title', 'Author(s)', 'Journal', 'Cited (articles)', 'Cited (cases)', 'Accessed', 'Topics']))
                        stats_index +=4
                        title_index += 4
                        topic_div_index +=1
                        page_name.append(cur_page)
                        #Check that next paper exists:
                        x_path_title = '//*[@id="save_results"]/div/div/div/div[' + str(title_index) + ']/div[2]/dt[1]/div'
                        element = driver.find_elements_by_xpath(x_path_title)
                df.to_csv(create_path('author_papers', '{}_{}_papers.csv'.format(full_name, school)))
                time.sleep(3)
            print('No remaining pages to scrape for {}.'.format(fm_name + ' ' + last_name))  
        if not df_sub.empty:
            my_dict = {'Person': [full_name], 'School': [school], 'Type': ['number']}
            name_data = pd.DataFrame(my_dict)
            df_sub = pd.concat([name_data, df_sub], sort = False, axis = 1)
            main_df = pd.concat([main_df, df_sub])
                    
skip_df.to_csv(create_path('skipped_names', '{}_skipped.csv'.format(school)))
main_df.replace(0, 'na')
main_df.to_csv(create_path('school_stats', '{}_stats.csv'.format(school)))