#!/usr/bin/env python
"""flag_autor_cut_off.py

This module contains a function that flags
the author cut-off variables.
"""

import pandas as pd

__author__ = "Martin Bolger"
__date__ = "February 21th, 2021"

def flag_author_cut_off(start_year, bbcite_first_year, journal_exclude, journal, word_exclude, title, bbcite_exclude, bbcite):
    flag = 0
    if not start_year == "":
        if start_year > bbcite_first_year:
            flag = 1
    if journal_exclude:
        if journal_exclude == journal:
            flag = 1
    if word_exclude:
        if word_exclude in title:
            flag = 1
    if bbcite_exclude:
        bbcite_exclude_list = bbcite_exclude.split(", ")
        for bbcite_exclude_item in bbcite_exclude_list:
            if not bbcite_exclude_item == "":
                if bbcite_exclude_item == bbcite:
                    flag = 1
    return flag