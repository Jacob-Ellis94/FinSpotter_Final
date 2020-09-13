import spacy
import fuzzywuzzy
import pandas as pd
import xlrd
import re
from cleanco import  cleanco,prepare_terms, basename


def get_all_companies(): # Consolidates all calls from other functions.
    legal_names, tickers = get_wilshire_names()
    cleaned_wilshire = clean_names(legal_names)  # FULL LIST OF COMPANIES IN WILSHIRE 5000
    # print (cleaned_wilshire)
    # print(tickers)
    cleaned_fortune = get_fortune500()
    cleaned_forbes = get_forbes2000()
    # print(cleaned_forbes)
    all_companies = []
    all_companies.append(cleaned_forbes)
    all_companies.append(cleaned_fortune)
    all_companies.append(cleaned_wilshire)
    all_companies = all_companies[0]
    return all_companies

def get_wilshire_names():
    firstDF = pd.read_excel(r'C:\Users\king-\PycharmProjects\Fin_Spotter\wilshire_5000_stocks.xlsx')
   # print(firstDF)
    column = firstDF["Name"]  # Turn excel file into dataframe
    tickers = firstDF["Ticker"]
    nested_names = column.values.tolist()  # Convert column to list of strings
    tickers = tickers.values.tolist()

    name_list = []
    count = 0
    for name in nested_names:
        name_list.append(name)
    name_list=clean_names(name_list) #Clean off legal suffix from names
    #print(name_list)
    return name_list, tickers

def get_fortune500():
    firstDF = pd.read_excel(r'C:\Users\king-\PycharmProjects\Fin_Spotter\Fortune500.xlsx')
    #print(firstDF["COMPANY NAME"])
    column = firstDF["COMPANY NAME"]
    fortune_names = column.values.tolist()  # Convert column to list of strings
    return fortune_names

def get_forbes2000():
    firstDF = pd.read_excel(r'C:\Users\king-\PycharmProjects\Fin_Spotter\Forbes2000.xlsx')
    #print(firstDF["COMPANY NAME"])
    column = firstDF["Company Name"]
    fortune_names = column.values.tolist()  # Convert column to list of strings
    #print(fortune_names)
    return fortune_names


def clean_names(names_in):
    clean_names = []
    terms = prepare_terms()
    for name in names_in:
        if (type(name)!='str'):
            name = str(name)
        name = re.sub("Inc.", "", name) # Used to remove legal suffixes
        name = re.sub("Ltd.", "", name)
        name = re.sub("Corp.", "", name)
        name = re.sub("Co.", "", name)
        name = re.sub('[^A-Za-z0-9]+',' ',name)
        clean_names.append(basename(name, terms, prefix=False, middle=False, suffix=True))
    return clean_names

