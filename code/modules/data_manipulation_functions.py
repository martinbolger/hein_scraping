#I don't think this is used anymore, 
#but it converted numbers like 1,000 to ints or floats
#I think I found a better way to do it
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

#This converts a zipped list into a dictionary
#It skips missing elements. 
#The function wouldn't be necessary if all the entries were always present
def create_dataframe_dict(my_list):
    #, person, school, data_type):
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

#Removes commas from all values in a row of a dataframe
def remove_commas(df1):
    for col in df1.columns:
        df1[col] = df1[col].str.replace(',', '')
    return df1

#This function checks to see if a file with the papers from a professor has already been created
#If it has, their name is skipped (their data is not rescraped)
def check_files(fm_name, last_name, current_files):
    done = False
    for cur_file in current_files:
        if fm_name.lower() in cur_file.lower() and last_name.lower() in cur_file.lower():
            done = True
            break
    return done

#This function checks to see if a dataframe for a specific stat and school already exists
#This allows the program to pick up where it left off if it stops
def check_df(current_stats, school_name):
    file = ''
    for cur_stat in current_stats:
        if school_name in cur_stat.lower():
            file = cur_stat
            break
    return file