
# This file uses the FuzzyWuzzy library to make checks on company names. Used as part of the Named Entity Recognition
# phase of the program. This is seen across all blog function files.


from fuzzywuzzy import fuzz, process

def fuzzy_check(entity, company_list):
    match = False
    score = process.extractOne(entity, company_list) # Uses Fuzzy to search list of companies
    if (score[1]>92):
        match = True # Recognises acceptable match
        #print(score)
    return match, score[0] # returns both the word as it appears in text, and the matched company title (standardised)

def entity_fuzz(first, second):
    score = fuzz.ratio(first,second)
    if score > 80:
        return True