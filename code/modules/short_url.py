#!/usr/bin/env python
"""create_url.py

This function removes the protocol identifier 
from a URL to create a short version of the URL.
The examples in the first if statement are from 
the previous datasets. More examples may need to be added.

Input:
url_data: dataframe
    This is the dataframe with the URL data.

url_var: string
    This is the name of the URL variable on 
    the url_data dataframe.

Output:
urls_df: dataframe
    This is a dataframe with the updated URL data. It is
    saved as a CSV and returned.
"""

from urllib.parse import urlparse

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

def short_url(url_data, url_var ):
    url_data["Short URL"] = url_data[url_var].apply(lambda x: urlparse(x).netloc)
    return url_data
    # short_url_list = []
    # for url in url_data[url_var]:
    #     if '.edu' in url:
    #         end = '.edu'
    #     elif '.ca' in url:
    #         end = '.ca'
    #     elif '.ac.uk' in url:
    #         end = '.ac.uk'
    #     elif '.hk' in url:
    #         end = '.hk'
    #     elif '.ac.il' in url:
    #         end = '.ac.il'
    #     elif '.yu' in url:
    #         end = '.yu'
    #     if 'https://www.' in url:
    #         new_url = url.split('https://www.')[1].split(end)[0]
    #     elif 'http://www.' in url:
    #         new_url = url.split('http://www.')[1].split(end)[0]
    #     elif 'https://www1.' in url:
    #         new_url = url.split('https://www1.')[1].split(end)[0]
    #     elif 'https://www2.' in url:
    #         new_url = url.split('https://www2.')[1].split(end)[0]
    #     elif 'www.' in url:
    #         new_url = url.split('www.')[1].split(end)[0]
    #     elif 'https://' in url:
    #         new_url = url.split('https://')[1].split(end)[0]
    #     elif 'http://' in url:
    #         new_url = url.split('http://')[1].split(end)[0]
    #     short_url_list.append(new_url+end)
