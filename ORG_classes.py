
#This file holds the main classes used in the backend functions. Each class has been explained in greater depth
# in the report which accompanies this program.


class Article_company:
    def __init__(self, company='DEFAULT', present_name = 'DEFAULT', sentences=['DEFAULT'], art_vader = 0):
        self.company_name = company
        self.present_name = present_name
        self.sentence_list = sentences
        self.art_average = art_vader

class Article_obj:
    def __init__(self, title = 'DEFAULT', URL = 'DEFAULT', company_list = ''):
        self.title = title
        self.URL = URL
        self.company_list = company_list

class Full_company:
    def __init__(self, company='DEFAULT', sentences=['DEFAULT'], URL_list = [], micro_vader = 0, macro_vader= 0, temp_vader=0):
        self.company_name = company
        self.sentence_list = sentences
        self.URL_list = []
        self.micro_average = micro_vader
        self.macro_average = macro_vader
        self.temp_average = temp_vader


class thing:
    def __init__(self, first,second,third,popup=0, popList=[]):
        self.company_name = first
        self.micro_average = second
        self.macro_average = third