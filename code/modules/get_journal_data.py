import pandas as pd

def get_journal_data(in_df):
    jname_series = in_df["Journal"]
    index_series = in_df["ID"].reset_index(drop = True)
    # Create the output df
    df = pd.DataFrame(columns = ['ID', 'Journal Name', 'Vol', 'Issue', 'Pages'])
    index = 0
    for jname_string in jname_series:
        data_stream = dict.fromkeys(['ID', 'Journal Name', 'Vol', 'Issue', 'Pages'], '')
        if jname_string != '':
            data_stream["ID"] = index_series.iloc[index]
            data_stream['Journal Name'] = jname_string.split(', Vol.', 1)[0]
            jelements = 'Vol. ' + jname_string.split('Vol.', 1)[1]
            jelement_list = jelements.split(',')

            for elm in jelement_list:
                if 'Vol.' in elm:
                    data_stream['Vol'] = elm.split('Vol.')[1].strip()
                elif 'Issues' in elm:
                    data_stream['Issue'] = elm.split('Issues')[1].strip()
                elif 'Issue' in elm:
                    data_stream['Issue'] = elm.split('Issue')[1].strip()
                elif 'pp.' in elm:
                    data_stream['Pages'] = elm.split('pp.')[1].strip()
        df = df.append(pd.DataFrame([list(data_stream.values())], columns = ["ID", 'Journal Name', 'Vol', 'Issue', 'Pages']), sort=False)
        index += 1
    return df