#This file holds various functions used to transform, or analyse data at various stages.
# Comments will be places at sections of interest.

from ORG_classes import Article_company, Article_obj, Full_company
import spacy
import en_core_web_sm
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from Fuzzy_functions import entity_fuzz
import os
import re
import pickle
import time
from operator import itemgetter, attrgetter
import glob, sys
from Fuzzy_functions import fuzzy_check
from UKInvestor_functions import UKInvestor_writer
from Investing_functions import Investing_writer
from FinanceBrokerage_functions import FinanceBrokerage_writer
from Motley_functions import Motley_writer
nlp = en_core_web_sm.load()

new_words = { # Attempt to alter lexicon of VADER)
    'underperforms': -4.0,'plummets': -3.8,'slipped': -2.8,'mixed performance': -2.4,
    'outperformed': 2.0,'surge': 1.5,'shares climb': 3.0,'soaring': 3.0,'stock falls': -2, 'short': -2.0,
    'minor gains':-1, 'shorted': -3.0, 'hit during lockdown': -2
}
vader = SentimentIntensityAnalyzer()
vader.lexicon.update(new_words)

def All_blogs(): # This function is used to make it easier for UI to interact with the backend functions.
    print("START OF FUNCTIONS")
    Motley_writer()
    UKInvestor_writer()
    Investing_writer()
    FinanceBrokerage_writer()
    #This section imports all the writers for each respective blog.
    text_fileSorter() #This trims number of files to most recent 100

    Art_object_maker() # Makes article objects from text files
    Art_obj_fileSorter() #Limits article objects to most recent 100

    results= full_merger()#Merges all references to a company into single object (returns list of Full_company objects)
    return results


def Art_object_maker():
    pickle_in = open("company_list.pickle", "rb")
    all_companies = pickle.load(pickle_in)  # Takes in list of companies which has been pickled

    directory = '.\\TextFiles'
    for entry in os.scandir(directory):
        existing_article = False
        NER_list = []
        file_name1 = os.path.basename(entry) # Strips file to base name (title of article)
        pickled_articles = '.\\Article_objects'
        for article in os.scandir(pickled_articles):
            file_name2 = os.path.basename(article.path) # Strips file to base name (title of article)
            name1 = file_name1.rsplit('.', 1)[0]
            name2 = file_name2.rsplit('.', 1)[0]
            if name1 == name2:
                existing_article = True # Check to see if file already has an Article_object

        if existing_article == True:
            #print ("ARTICLE EXISTS")
            continue

        if (entry.path.endswith(".txt")):
            with open(entry, 'r') as f:
                output = f.read()
            doc = nlp(output)  # Read in .txt file and create doc object
            Art_company_list = []
            label_types = ['ORG', 'WORK_OF_ART', 'PERSON']
            counter = 0
            for ent in doc.ents:  # NER stage
                if 'https' in ent.text:  # Removes initial URL in .txt file from being recognised as entity.
                    continue
                elif ent.label_ in label_types:
                    result = fuzzy_check(ent.text, all_companies)
                    if result [0]:
                        NER_list.append((result[1],ent.text)) # Creates tuple (Company name - name present)
                        #print(ent.text +" Count = ", counter)
        else:
            continue
            #print("ERROR")

        URL = doc.text.split('\n')[1] # Grabs URL from text document.
        title = doc.text.split('\n')[0]

        unique_orgs = list(set(NER_list))  # Creates unique list of mentioned companies
        unique_orgs.sort()  # Puts them into alphabetical order
        i = 0
        for NE in unique_orgs:
            new_company = Article_company(NE[0], NE[1]) # NE stands for Named Entity here (see Fuzzy_functions.py)
            sent_list=[]
            art_avg = 0
            for sent in doc.sents:
                if NE [1] in sent.text:
                    sentences = ((sent.text, vader.polarity_scores((sent.text))['compound'])) #Here is where scores made
                    sent_list.append(sentences)
                    score = vader.polarity_scores((sent.text))['compound']
                    art_avg += score # This provides a running total so that averages can be made later in program
                    #print (sentences)
            new_company.sentence_list = list(sent_list) # Writes all sentences to list
            new_company.art_average = round(art_avg / len(new_company.sentence_list),3)# provides average sentiment for article
            Art_company_list.append(new_company)
            i+=1

        new_article = Article_obj(title, URL) # Creates article object with all companies in an article
        new_article.company_list = list(Art_company_list) #Assignment of list of company objects
        title = re.sub('[^A-Za-z0-9]+', '_', title)  # Strip special characters for saving file name
        #This naming convention also makes it possible to check if an article object already exists from a .txt file
        #title. Both are named similarly.

        pickle_out = open(
            f".\\Article_objects\\{title}.pickle",
            "wb")
        pickle.dump(new_article, pickle_out)  # Outputs pickled list of article objects for comparisons.
        pickle_out.close()


def full_merger():
    full_list=[]
    for obj in os.scandir('.\\Article_objects'): #Iterates through article object directory
        pickle_in = open(obj, "rb")
        article = pickle.load(pickle_in)
        found = False
        for company in article.company_list:
            if len(full_list)<1: # If list is empty, then first Full_company created
                new_obj = Full_company(company.company_name, company.sentence_list)
                new_obj.URL_list.append((article.title, article.URL))
                new_obj.temp_average += company.art_average
                full_list.append(new_obj)
                continue

            for full_org in full_list: #Check to see if a full company object exists
                if full_org.company_name == company.company_name:
                    found = True
                    temp = full_org
                    break

            if found == False: #If no company exists already - then create a new Full_company for it
                new_obj = Full_company(company.company_name, company.sentence_list)
                new_obj.URL_list.append((article.title, article.URL))
                new_obj.temp_average += company.art_average
                full_list.append(new_obj)
                #print("NEW")
                #print(company.company)

            if found == True: #If that company exists, that information is added to the Full_company object
                temp.sentence_list.extend(company.sentence_list) #Temp used to hold that position from earlier section
                temp.URL_list.append((article.title, article.URL))
                temp.temp_average += company.art_average #Used to find sum of article averages
                #print("MATCHED")
                #print(company.company)

    for company in full_list:
        macro_valence = 0
        for sent in company.sentence_list:
            macro_valence += sent[1]
            company.macro_average = round(macro_valence / len(company.sentence_list),3)
            #Gives average for ALL sentences in all articles

        # print (f"TEMP = {company.temp_average}")
        # print(f"LENGTH = {len(company.URL_list)}")
            company.micro_average = round(company.temp_average / len(company.URL_list), 3) # Rounds average to 3 places

    full_list.sort(key=lambda x: x.macro_average, reverse=True) # Sorts list of companies on macro_average
    return full_list

def save_report(full_list): #Reduncancy, UI does not implement show old reports, though reports can be saved
    #Kept in as proof that improvements could be made with longer time allocation.
    current_date = time.strftime("%Y-%m-%d")
    #print(current_date)
    count = 0
    while (os.path.isfile(f".\\Final_Reports\\{current_date}_{count}.pickle")):
        count+=1
    pickle_out = open(f".\\Final_Reports\\{current_date}_{count}.pickle",
                      "wb")
    pickle.dump(full_list, pickle_out)  # Outputs pickled list of article URLs for comparisons.
    pickle_out.close()

def Art_obj_fileSorter():
    # Removes all but most recent 100 files in a directory - Used to trim Article_objects & text files
    # Keeps analysis relevant by excluding older data
    fileData = {}
    for entry in os.scandir("Article_objects"):
        fileData[entry] = os.stat(entry).st_mtime # Used to sort by date modified

    sortedFiles = sorted(fileData.items(), key=itemgetter(1))

    keep = 100 # This value determines how many files to keep, in this case, most recent 100 files
    if len(sortedFiles)!= 100:
        delete = len(sortedFiles) - keep
        for x in range(0, delete):
            os.remove(sortedFiles[x][0])
            print(f"REMOVED {x}")

def text_fileSorter():
    # Removes all but most recent 100 files in a directory - Used to trim Article_objects & text files
    # Keeps analysis relevant by excluding older data
    fileData = {}
    for entry in os.scandir("TextFiles"):
        fileData[entry] = os.stat(entry).st_mtime # Used to sort by date modified

    sortedFiles = sorted(fileData.items(), key=itemgetter(1))

    keep = 100 # This value determines how many files to keep, in this case, most recent 100 files
    if len(sortedFiles)!= 100:
        delete = len(sortedFiles) - keep
        for x in range(0, delete):
            os.remove(sortedFiles[x][0])
            print(f"REMOVED {x}")

