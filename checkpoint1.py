# Author: Jacob Ellis
# Date: 31/08/2020
# This program has been created by Jacob Ellis as part of the MSc Applied Computing project 2020.
# The objective of this program is to parse 100 articles, found from various financial blogs, and to identify named
# companies for further analysis. Once companies have been identified, sentiment analysis on the sentences in which
# they appear can be calculated accordingly. More details can be found in the accompanying report.
#
# This main.py file is primarily used to create the UI elements, most backend functions have been written in other .py
# files in this project. For file auditing purposes, here is a list of the files that should be found with this one:
#(Directory folders) - Article_objects, Final_reports, Fonts, TextFiles
# (Image files) - bar_graph.png, light.jpg
# (.py files) - FinanceBrokerage_functions, Fuzzy_functions, Investing_functions, Motley_functions, ORG_classes,
# Populate_list_functions, UKInvestor_functions
# (pickled objects) - company_list.pickle
#


import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.factory import Factory
from kivy.uix.recycleview import RecycleView
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.uix.progressbar import ProgressBar
##################################################################################
# Kivy imports above
##################################################################################
from Populate_list_functions import All_blogs
from ORG_classes import Full_company
import matplotlib.pyplot as plt
import pandas as pd
import threading
import time
import os

result = []

# This section imports fonts for use in the UI.
LabelBase.register(name="Monoton",
                   fn_regular= ".\\Fonts\\Monoton-Regular.ttf")
LabelBase.register(name="Roboto",
                   fn_regular= ".\\Fonts\\Roboto-Regular.ttf")
LabelBase.register(name="Arg",
                   fn_regular= ".\\Fonts\\Aaargh.ttf")
LabelBase.register(name="Rubik",
                   fn_regular= ".\\Fonts\\Rubik-Regular.ttf")
LabelBase.register(name="Oswald",
                   fn_regular= ".\\Fonts\\Oswald-Regular.ttf")



class WelcomeWindow(Screen):
    pass #Kivy uses objects and lots of inheritence to implement its UI, these windows are self explanatory.

class MainWindow(Screen):
    pass

class AnalysisWindow(Screen):
    result = ObjectProperty()
    def startAnalysis(self):#This function is executed once a button is pressed (see pageDesign -> AnalysisWindow)
        self.manager.current = 'Loading'  # Here is where I have tried to move to loading screen while func runs
        app = App.get_running_app() # This accesses the instance of App class
        count = 0
        dictList = []
        results= All_blogs() #This runs the entire backend process for collecting data/analysis. Returns companies.
        app.company_results = results #Saves this to a kivy property for use in other screens (see MyMainApp class)

        for company in results: # Recycle view only accepts a dictionary as data input - this constructs that
            entry = {'companyName': company.company_name, 'microAvg': "Micro: " + str(company.micro_average),
            'macroAvg': "Macro: " + str(company.macro_average), 'popup': company.company_name,
            'sentences': (company.sentence_list), 'URLs': company.URL_list, 'idx': count}
            count += 1
            dictList.append(entry)

        app.data = dictList # Again, a kivy property in MyMainApp allows this to be used in other screens.
        self.set_screen()

    def executeFunc(self):
        self.manager.current = 'Loading'  # Here is where I have tried to move to loading screen while func runs
        t1 = threading.Thread(target=self.startAnalysis)  # Here is where I have tried to thread the function
        t1.start()

    @mainthread
    def set_screen(self):
        self.manager.current = 'output'


    pass

class LoadingWindow(Screen):
    pass

class LoadingBar(Popup):

    def __init__(self, **kwa):
        super().__init__(**kwa)

        self.progress_bar = ProgressBar()
        self.title='Analysis in Progress...'
        self.title_size = 25
        self.content=self.progress_bar
        self.bind(on_open=self.puopen)
        self.size_hint = (1,.5)

    def pop(self, instance):
        self.progress_bar.value = 1
        self.popup.open(size=(200,200))

    def next(self, dt):
        if (self.progress_bar.value >= 100):
            self.dismiss()
            return False
        self.progress_bar.value += 1

    def puopen(self, instance):
        instance.size = (200,200)
        Clock.schedule_interval(self.next, 1/2)






class OutputWindow(Screen):
    result = ListProperty()
    img = ObjectProperty()
    def make_graph(self): # This section creates a simple bar graph to display top ten companies
        companies = []
        count = 0
        app = App.get_running_app()
        result = app.company_results
        # for comp in result:
        #     print(comp.sentence_list) # Used to debug and see all sentences for all companies

        while (count < 10):
            companies.append(result[count])
            count+=1
        #The following is a very standard matplotlib implementation, not much to comment on
        data = pd.DataFrame([comp.macro_average for comp in companies],
                            index=[comp.company_name for comp in companies],
                            columns=['Sentiment Score'])
        data.plot(kind='barh', legend=None,color=(0.6,0.8,.2,1))
        #plt.bar(y_pos, height, color=(0.2, 0.4, 0.6, 0.6))
        plt.xlim(0,1) #Locked scale instead of relative
        plt.suptitle('Top ten companies ordered by sentiment', fontsize=16)
        plt.gca().invert_yaxis()
        #leg = plt.legend(loc='lower right')
        plt.savefig('bar_graph_top.png',bbox_inches='tight', dpi=100) # Saves bar graph as an image for display later
        img = Image(source='bar_graph_top.png')
        img.reload()

    pass



class GraphWindow_top(Screen):
    img_src = StringProperty('.\\bar_graph_top.png')

    def make_graph(self):  # This section creates a simple bar graph to display top ten companies
        companies = []
        app = App.get_running_app()
        result = app.company_results
        # for comp in result:
        #     print(comp.sentence_list) # Used to debug and see all sentences for all companies
        count = len(result)-1
        while (count > len(result)-11):
            companies.append(result[count])
            count -= 1
        # The following is a very standard matplotlib implementation, not much to comment on
        data = pd.DataFrame([comp.macro_average for comp in companies],
                            index=[comp.company_name for comp in companies],
                            columns=['Sentiment Score'])
        data.plot(kind='barh', legend=None, color=(0.7,0,0,1))
        plt.xlim(-1, 0)  # Locked scale instead of relative
        plt.suptitle('Bottom ten companies ordered by sentiment', fontsize=16)
        #plt.gca().invert_yaxis()
        #leg = plt.legend(loc='upper left')

        plt.savefig('bar_graph_bottom.png', bbox_inches='tight', dpi=100)  # Saves bar graph as an image for display later

        img = Image(source='bar_graph_bottom.png')
        img.reload()




    pass

class GraphWindow_bottom(Screen):
    #img_src = StringProperty('.\\bar_graph_bottom.png')
    pass


class RV(RecycleView): #Possibly the hardest part of the UI, this forms the base component
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)


class HelpPopup(Popup): #Popup screen for help button - populated in pageDesign .kv file
    pass

class DataPopup(Popup): #Similar to above, but for 'Sentences' button
    sentences = ListProperty()
    target_idx = NumericProperty()
    target_rv = ObjectProperty()

    second = StringProperty()
    first = StringProperty()


class URLPopupRVRow(BoxLayout): #Similar to above, but for 'Articles' button
    sentences = ListProperty()
    target_idx = NumericProperty()
    target_rv = ObjectProperty()
    text = StringProperty()
    link = StringProperty()

class URLPopup(Popup): #As above
    sentences = ListProperty()
    URLs = ListProperty()
    target_idx = NumericProperty()
    target_rv = ObjectProperty()
    link = StringProperty()
    text = StringProperty()

class PopupRVRow(BoxLayout):
    sentences = ListProperty()
    score = StringProperty()
    text = StringProperty()
    URLs = ListProperty()
    target_idx = NumericProperty()
    target_rv = ObjectProperty()
    link = StringProperty()
    text = StringProperty()

class RecycleViewRow(BoxLayout): #Most logic and layout for these components found in .kv file

    # text = StringProperty()
    # other = StringProperty()
    companyName = StringProperty()
    microAvg = StringProperty()
    macroAvg = StringProperty()
    popup = StringProperty()
    sentences = ListProperty()
    second = StringProperty()
    idx = NumericProperty()
    URls = ListProperty()



class WindowManager(ScreenManager): #Foundational widget - allows page navigation.
    result = ListProperty()
    pass


class MyImageWidget(Widget): # Particularly tricky widget used to update the bar chart image to current one
    def __init__(self,**kwargs): #LOTS of time spent trying to implement this - before image was generated from
        super(MyImageWidget,self).__init__(**kwargs) # the previous program run.
        self.image = Image(source='bar_graph_top.png')
        self.image.size = (1000,700)
        self.image.pos = (-100,0)
        self.add_widget(self.image)
        Clock.schedule_interval(self.update_pic,1) #this took HOURS to figure out

    def update_pic(self,dt):
        self.image.reload()

class MyImageWidget2(Widget): # Particularly tricky widget used to update the bar chart image to current one
    def __init__(self,**kwargs): #LOTS of time spent trying to implement this - before image was generated from
        super(MyImageWidget2,self).__init__(**kwargs) # the previous program run.
        self.image = Image(source='bar_graph_bottom.png')
        self.image.size = (1000,700)
        self.image.pos = (-100,0)
        self.add_widget(self.image)
        Clock.schedule_interval(self.update_pic,1) #this took HOURS to figure out

    def update_pic(self,dt):
        self.image.reload()





class MyMainApp(App): #This class constructs the GUI as a whole out of its components(unable to explain past that)
    company_results = ObjectProperty([]) # Properties used to pass data between widgets.
    data = ObjectProperty([])
    def build(self):
        kv = Builder.load_file("pageDesign.kv") #This part includes the code written in the .kv file
        return kv

if __name__ == "__main__":
    MyMainApp().run()