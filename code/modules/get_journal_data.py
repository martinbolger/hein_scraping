import pandas as pd
import re

def get_journal_data(in_df):
    in_df["Journal Name"] = in_df["Journal"].apply(lambda x: x.split(', Vol.', 1)[0] if x != '' else '')
    vol_list = in_df["Journal"].apply(lambda x: re.search(r"Vol. (\d*-?\d*)", x))
    in_df["Vol"] = vol_list.apply(lambda x: x.group(1) if x else '')
    issue_list = in_df["Journal"].apply(lambda x: re.search(r"Issues? (\d*-?\d* \(.*\))", x))
    in_df["Issue"] = issue_list.apply(lambda x: x.group(1) if x else '')
    in_df['Pages'] = in_df["Journal"].apply(lambda x: x.split('pp.')[1].strip() if x != '' else '')
    return in_df
