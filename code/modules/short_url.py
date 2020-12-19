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
import tldextract

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

def short_url(url_data, url_var ):
    url_data["URL Var Clean"] = url_data[url_var].apply(lambda x: x.split(" ")[0] if " " in x else x)
    url_data["Short URL"] = url_data["URL Var Clean"].apply(lambda x: tldextract.extract(x).domain + "." + tldextract.extract(x).suffix)
    return url_data
