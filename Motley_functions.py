# Each blog has a .py file containing the functions used to parse each webpage. Extraction methods are similar,
# but differ slightly as the page structure displays text differently. In the interests of brevity, I will
# use this header for each of the blog function files.


import requests
from urllib.request import Request, urlopen
import urllib3
from bs4 import BeautifulSoup
import time
import pickle
from ORG_classes import Article_company, Article_obj
import re
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()
import spacy
nlp = spacy.load('en_core_web_sm')
from Fuzzy_functions import fuzzy_check
from pathlib import Path
from operator import itemgetter, attrgetter
import glob, sys
#from Populate_list_functions import full_merger, save_report, text_fileSorter, Art_obj_fileSorter




def Motley_writer():
    BaseUrl = "https://www.fool.co.uk/recent-headlines/"  # base url from which to find articles
    SecondPage = "https://www.fool.co.uk/recent-headlines/page/2/"  # Second page for Motley Fool
    ThirdPage = "https://www.fool.co.uk/recent-headlines/page/3/" # Third page for Motley
    URLlist = Motley_URL_lister(BaseUrl) + Motley_URL_lister(SecondPage) + Motley_URL_lister(ThirdPage) # Function created to reduce code, makes URL list

    # print("FULL URL LIST: ", URLlist)
    # print("Length: ", len(URLlist))

    count = 0
    for url in URLlist:  # Iterates over all URLs in list for writing to .txt
        title = URLlist[count][0]
        title = re.sub('[^A-Za-z0-9]+', '_', title) # Strip special characters for saving file name
        if  (os.path.isfile(f'.\\TextFiles\\{title}.txt')):
            #Checks to see if file already exists before sending requests
            # print(f"{title}")
            # print("FOUND")
            count +=1
            continue
        else: # If file does not already exist
            html = URLlist[count][1]
            req = Request(html, headers={'User-Agent': 'Mozilla/5.0'})  # Defines request parameters
            webpage = urlopen(req).read()
            count += 1
            # print(html)
            MotleyPage = BeautifulSoup(webpage, 'html.parser')# Beautiful soup object from HTML file
            article = MotleyPage.find('article', class_='large-8 columns clearfix')# Find particular section of webpage
            full_content = article.find('section',
                                        {'id': "full_content"})  # Creates object for pulling content from section
            inner_content = full_content.find_all('p')  # pulls just text from full_content object
            limit = len(inner_content) - 11  # Removes boilerplate membership text
            cursor = 0
            print("HERE")
            # Writes webpage text in to a .txt file
            with open(f'TextFiles\\{title}.txt', 'w+') as f:
                f.write(url[0] + '\n' + url[1]+'\n')
                while cursor < limit:
                    # print(inner_content[cursor].text)
                    f.write(u'' + inner_content[cursor].text)
                    cursor += 1


def Motley_URL_lister (url):
    html = url # base url from which to find articles
    req = Request(html , headers={'User-Agent': 'Mozilla/5.0'}) # Masks webcrawler as browser
    webpage = urlopen(req).read()
    # Done to avoid the forbidden code from server
    #print(webpage)
    soup = BeautifulSoup(webpage, 'html.parser') # Tell beautiful soup to use particular parser
    #print(soup.prettify()) # Introduces indents for HTML code for ease of visualisation
    artlist = soup.find('ul', class_='article-list') #Finds list of article URLs
    #print(artlist.prettify())
    URLlist = []
    headlines1 = artlist.findAll('h2')  # list of headlines on webpage
    for article in headlines1:  # Loop for analysing <a>
        link = article.find('a')['href']  #
        anchors = article.findAll('a')  # finds all anchor tags
        for a in anchors:
            text = str(a.string)  # Pulls text from href
            URLlist.append((str(a.string), link)) # Creates tuple with article title and URL

    return URLlist





