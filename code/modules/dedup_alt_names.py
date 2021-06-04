#!/usr/bin/env python
"""dedup_alt_names.py

Deduplicates the list of alt names.
"""

import re 

def dedup_alt_names(alt_names):
    # Create a list of the alt names
    alt_name_list = alt_names.split(",")
    # Strip the names and remove the part after a semi colon if it exists
    alt_name_list = [x.strip().split(";")[0] for x in alt_name_list]
    return ', '.join(set(alt_name_list))