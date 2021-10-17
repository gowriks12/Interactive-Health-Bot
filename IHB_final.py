import pandas as pd
import os
import csv
import nltk
from nltk.stem import PorterStemmer
import speech_recognition as sr
from nltk.util import bigrams,trigrams,ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import pyttsx3
import time
import datetime
from pattern.en import conjugate, lemma, lexeme,PRESENT,SG
from itertools import combinations
from firebase import firebase
from tkinter import *
from tkinter.ttk import Frame
from tkinter import ttk
from tkscrolledframe import ScrolledFrame
import difflib
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from jellyfish import soundex
from jellyfish import metaphone
import random
from os import system, name 
import numpy as np


#Reading the DS18B20 sensor from devices list
def sensor():
    for i in os.listdir('/sys/bus/w1/devices'):
        if i != 'w1_bus_master1':
            ds18b20 = i
    return ds18b20

#Reading the temperature from the sensor
def read(ds18b20):
    location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    celsius = temperature / 1000
    farenheit = (celsius * 1.8) + 32
    return celsius, farenheit

#Original function to display temp and classify the type of fever
def loop(ds18b20):
    print("Place the sensor in the armpit")
    time.sleep(2)
    print("Recording the body temp")
    time.sleep(60)
    if read(ds18b20) != None:
        print("Current Body temperature in celsius : %0.3f C" % read(ds18b20)[0])
        print("Current Body temperature in fahrenheit: %0.3f F" % read(ds18b20)[1])
        if (read(ds18b20)[1] < 98.0):
            k="No fever"
        elif ((read(ds18b20)[1] >= 98.0) and (read(ds18b20)[1] < 102.0)):
            k="mild fever"
        elif ((read(ds18b20)[1] >= 102.0) and (read(ds18b20)[1] < 106.0)):
            k="high Fever"
        else:
            k="Very High Fever"
    return k

#Classify the fever type
def fever_check(tem):
        print("Current Body temperature in fahreinheit: %0.3f F" % temp)
        if (temp < 98.0):
            k="No fever"
        elif ((temp >= 98.0) and (temp< 102.0)):
            k="mild fever"
        elif ((temp >= 102.0) and (temp < 106.0)):
            k="high fever"
        else:
            k="Very high fever"
        return k

#serialNum = sensor()
temp=0
cond=""
class SymptomRecognizer(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.parent=parent
        self.frame = Frame(self.parent)
        self.sf = ScrolledFrame(parent, width=800, height=500)
        self.sf.bind_arrow_keys(parent)
        self.sf.bind_scroll_wheel(parent)
        self.inner_frame = self.sf.display_widget(Frame)
        self.sf.pack()

        self.stemmed_words = []
        self.recognizer = sr.Recognizer()
        self.engine=pyttsx3.init()
        self.text=StringVar()
        self.text2=StringVar()
        self.output=[]
        self.stop_words=set(stopwords.words('english'))
        self.symptoms=[]
        self.y1=240
        self.le = preprocessing.LabelEncoder()
        self.model = RandomForestClassifier(n_estimators=10)
        self.inp=StringVar()
        self.data=dict()
        self.exit_counter=0
 
        self.read_symptoms_corpus()
        self.initUI()
        self.ask_symptoms()
        self.find_symptoms()

        self.check_symptoms()
        if self.exit_counter==1:
            self.inner_frame.after(2000,self.inner_frame.destroy())
            self.frame.after(3000,self.frame.destroy())
        if self.exit_counter==0:
            self.display_symptoms()
            self.classify_symptoms()
            self.inner_frame.after(2000,self.inner_frame.destroy())
            self.frame.after(3000,self.frame.destroy())

    def initUI(self):
        self.parent.title("Interactive Health Bot")
        self.pack(fill=BOTH, expand=True)
        label0=Label(self.inner_frame,text=" \t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t ",font=('Times New Roman',5))
        label0.pack()
        self.sf.pack()
        self.update()
        lable1=Label(self.inner_frame,text='Welcome to Interactive health bot',fg='black',bg='light blue',relief='solid',font={'Times New Roman',24,'bold'},pady=5,padx=5)
        #lable1.place(x=40,y=15)
        lable1.pack(side='top',anchor=CENTER)
        self.sf.pack()
        self.update()
        self.sf.yview('moveto', 15)
        self.engine.say('hello')
        self.engine.say('Welcome to interactive Health Bot')
        self.engine.runAndWait()
        
        label1a=Label(self.inner_frame,text="")
        label1a.pack()
        lable22=Label(self.inner_frame, text="Let's measure the body temperature", fg='black',bg='white',font={'times', 12, 'bold'}, anchor='w',pady=1)
        lable22.place(x=0, y=15)
        lable22.pack()
        self.sf.pack()
        self.update()
        self.sf.yview('moveto', 15)
        
        self.engine.say("Let's measure the body temperature")
        self.engine.say('Place the sensor on your armpit for a minute')
        self.engine.runAndWait()
        time.sleep(5)
        global temp
        global cond
        #store the temperature in fahrenheit in the variable temp
        #temp = read(serialNum)[1]
        
        temp=100
        self.data['Temperature']=temp
        #store the fever type in the variable cond
        cond = fever_check(temp)
        self.data['Condition']=cond
        lable23 = Label(self.inner_frame, text="Current body temperature is: {} F".format(temp), fg='black',bg='light blue',relief='raised',font={'times', 12, 'bold'}, anchor='w')
        lable23.place(x=25, y=80)
        lable23.pack()
        self.sf.pack()
        self.update()
        self.sf.yview('moveto', 15)
        
        self.engine.say('Current body temperature is')
        self.engine.runAndWait()
        self.engine.say(temp)
        self.engine.say('degree Fahrenheit')
        self.engine.runAndWait()
        lable24 = Label(self.inner_frame, text="You have: {}".format(cond.title()), fg='black', bg='white',font={'times', 12, 'bold'}, anchor='w')
        lable24.place(x=25, y=80)
        lable24.pack()
        self.sf.pack()
        self.update()
        self.sf.yview('moveto', 15)
        self.engine.say("You have")
        self.engine.say(cond)
        self.engine.runAndWait()
        label1b=Label(self.inner_frame,text="")
        label1b.pack()
        
        # if cond == "No fever":
        #     self.engine.say('No fever')
        # elif cond=="high fever":
        #     self.engine.say('You have High Fever')
        # elif cond == "mild fever":
        #     self.engine.say('You have Mild Fever')
        # else:
        #     self.engine.say('You have very high fever')
        
    def read_symptoms_corpus(self):
        symptoms_df = pd.read_csv('new_csv.csv', sep='\t')
        #self.symptom_words = list(symptoms_df["Symptoms"])
        self.symptom_words=list(symptoms_df)
        ps=PorterStemmer()
        for words in self.symptom_words:
            self.stemmed_words += ps.stem(words).split(",")
        new_words=[]
        for words in self.symptom_words:
            if words in self.stop_words:
                new_words.append(self.symptom_words-words)

        self.symptom_words=self.symptom_words+new_words
        self.stemmed_words = list(set(self.stemmed_words))
        self.stemmed_words = [item.strip() for item in self.stemmed_words]
        self.stemmed_words=list(self.stemmed_words)

    def ask_symptoms(self):
        while True:
            with sr.Microphone() as source:
                label2=Label(self.inner_frame,text="Please tell your symptoms",fg='black',font={'times',12,'bold'},anchor='w')
                label2.place(x=25,y=80)
                label2.pack(side='top')
                self.sf.pack()
                self.update()
                self.sf.yview('moveto', 80)
                print('Please tell your symptoms')
                self.update()
                self.engine.say('Please tell your symptoms')
                self.engine.runAndWait()
                audio = self.recognizer.record(source,duration=10)
                try:
                    self.text=self.recognizer.recognize_google(audio)
                    label3=Label(self.inner_frame,text="You said:",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                    label3.place(x=25,y=100)
                    label3.pack(side='top')
                    self.sf.pack()
                    self.update()
                    self.sf.yview('moveto', 100)
                    print("You said----> " + self.recognizer.recognize_google(audio))
                    display1=Message(self.inner_frame,text=self.text,relief='groove',fg='black',bg='light blue',width=450,font={'Times New Roman',12,'bold'},anchor='w')
                    display1.place(x=25,y=140)
                    display1.pack(side='top')
                    self.sf.pack()
                    self.update()
                    self.sf.yview('moveto', 140)
                    time.sleep(1)
                    self.engine.say('you said {}'.format(self.text))
                    self.engine.runAndWait()
                    break
                except sr.UnknownValueError:
                    print("Sorry  could not understand your voice")
                    label4=Label(self.inner_frame,text="Sorry  could not recognize your voice",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                    label4.place(x=25,y=100)
                    label4.pack(side='top')
                    self.sf.pack()
                    self.update()
                    self.pack(fill=BOTH,expand=True)
                    self.update()
                    self.sf.yview('moveto', 100)
                    self.engine.say('Sorry could not recognize your voice')
                    self.engine.runAndWait()
                    label4.after(1000, label4.destroy())
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    label5=Label(self.inner_frame,text="Sorry  could not understand audio",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                    label5.place(x=25,y=140)
                    label5.pack(side='top')
                    self.sf.pack()
                    self.update()
                    self.sf.yview('moveto', 140)
                    self.update()

    def find_symptoms(self):
        #self.text =  "I have  malaysia film"
        self.text=self.text.lower()
        text_tokens=word_tokenize(self.text)
        wordslist=[words for words in text_tokens if not words in self.stop_words]
        wordslist=list(wordslist)
        tagged=nltk.pos_tag(wordslist)

        def noun_parsing(tag):
            nouns=[]
            for words,pos in tag:
                if pos in ['NN','NNS','NNP','NNPS','JJ','JJR','JJS','RB','VB','VBD','VBN','VBG','VBP','VBZ']:
                    nouns.append(words)
            return nouns
        noun=noun_parsing(tagged)
        close_nouns=[]
        for i in noun:
            match_index = 0
            matched_symp = ""
            if fuzz.partial_ratio(i, self.stemmed_words) > 40:
                close_nouns.append(i)

        try:
            lexeme('')
        except:
            pass

        tenses=[]
        for i in noun:
            tenses+= lexeme(i)

        synonyms=[]
        for words in tenses:
            for syn in wordnet.synsets(words):
                for l in syn.lemmas():
                    synonyms.append(l.name())
        synonyms_set=set(synonyms)

        stemmed_synonyms=[]
        ps=PorterStemmer()
        for words in synonyms_set:
            stemmed_synonyms+= ps.stem(words).split(",")

        comb = combinations(tenses, 2)
        c=[]
        c+=[i for i in list (comb)]
        res = [' '.join(i) for i in c]

        text_ngrams=list(nltk.ngrams(text_tokens,2))
        text_ngrams3=list(nltk.ngrams(text_tokens,3))
        text_ngrams4=list(nltk.ngrams(text_tokens,4))
        text_ngrams5=list(nltk.ngrams(text_tokens,5))
        t_ngrams2=list(nltk.ngrams(stemmed_synonyms,2))
        t_ngrams3=list(nltk.ngrams(stemmed_synonyms,3))
        t_ngrams4=list(nltk.ngrams(stemmed_synonyms,4))
        t_ngrams5=list(nltk.ngrams(stemmed_synonyms,5))
        res2=[' '.join(i) for i in text_ngrams]
        res3=[' '.join(i) for i in text_ngrams3]
        res4=[' '.join(i) for i in text_ngrams4]
        res5=[' '.join(i) for i in text_ngrams5]
        r2=[' '.join(i) for i in t_ngrams2]
        r3=[' '.join(i) for i in t_ngrams3]
        r4=[' '.join(i) for i in t_ngrams4]
        r5=[' '.join(i) for i in t_ngrams5]
        lis=[]
        for i in res3+res4+res5:
            state=0
            i=i.split()
            while True:
                random.shuffle(i)
                new_sentence = ' '.join(i)
                if new_sentence in lis:
                    state+=1
                lis.append(new_sentence)
                if state==3:
                    break
        close_matches=[]
        for i in res2+res3+res4+res5+tenses+lis:
            for j in self.stemmed_words:
                #if 0<= int(soundex(i)[1:])-int(soundex(j)[1:])<=1:
                if 0<= int(soundex(i)[1:])-int(soundex(j)[1:])<=1:
                    if difflib.get_close_matches(metaphone(i),[metaphone(j)]):
                        if metaphone(j)[0]==metaphone(i)[0]:
                            close_matches.append(j)

                if fuzz.partial_ratio(metaphone(i), 'FLKM') > 70:
                #difflib.get_close_matches(metaphone(i),['FLKM']):
                    close_matches.append('phlegm')
                elif fuzz.partial_ratio(metaphone(i), 'MLS') > 70:
                #difflib.get_close_matches(metaphone(i),['MLS']):
                    close_matches.append('malaise')
                elif fuzz.partial_ratio(metaphone(i), 'FTK') > 70: 
                #difflib.get_close_matches(metaphone(i),['FTK','PRTK']):
                    close_matches.append('fatigue') 
                elif difflib.get_close_matches(metaphone(i),['LORJ']):
                    close_matches.append('lethargy')    
                elif fuzz.partial_ratio(metaphone(i), 'XLS') > 70:
                #difflib.get_close_matches(metaphone(i) , ['XLS','XL','XN','XLT','XR','SLS']):
                    close_matches.append("chills")

        print(set(close_matches))
        for w in tenses +res2+res3+res4+res5+r2+r3+r4+r5:
            if w in self.stemmed_words:
                self.output.append(w)
        self.output.extend(close_matches)
        self.output=list(set(self.output))
        print(self.output)

    def check_symptoms(self):
        #self.output=['malaise','high fever','headache','chest pain','phlegm']
        if cond.lower()=="high fever":
            if "high fever" in self.output:
                self.output.remove("high fever")
        elif cond.lower()=="mild fever":
            if "mild fever" in self.output:
                self.output.remove("mild fever")
        y=180
        def error_condition():
            y=180
            print("oops! Looks like we couldn't record any symptoms. Would you want to start over?")
            lable10=Label(self.inner_frame,text="oops! Looks like we couldn't record any symptoms. Would you want to start over?",fg='black',bg='white',font={'times',12,'bold'},width=300,anchor='w')
            #lable10.place(x=25,y=y)
            lable10.pack(side='top')
            self.sf.pack()
            self.update()
            self.sf.yview('moveto', y)
            self.engine.say("oops! Looks like we couldn't record any symptoms. Would you want to start over?")
            self.engine.runAndWait()
            print('yes or no?')
            label11=Label(self.inner_frame,text="YES or NO?",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
            y+=40
           # label11.place(x=25,y=y)
            label11.pack(side='top')
            self.sf.pack()
            self.update()
            self.sf.yview('moveto', y)
            self.engine.say("yes or no?")
            self.engine.runAndWait()
            count=0
            while True:
                count+=1
                with sr.Microphone() as source:
                    audio = self.recognizer.record(source,duration=5)
                    try:
                        self.text1=self.recognizer.recognize_google(audio)
                        if self.text1.lower()=='yes':
                            main_counter=1
                            self.quit()
                            main()
                        elif self.text1.lower()=='no':
                            print("Bye")
                            label12=Label(self.inner_frame,text="Bye!",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                            y+=40
                            label12.place(x=25,y=y)
                            label12.pack(side='top')
                            self.sf.pack()
                            self.update()
                            self.sf.yview('moveto', y)
                            self.engine.say("Bye")
                            self.engine.runAndWait()
                            time.sleep(2)
                            self.exit_counter=1
                            break
                        else:
                            pass
                    except sr.UnknownValueError:
                        print("Sorry  could not understand your voice")
                        label11a=Label(self.inner_frame,text="Sorry  could not recognize your voice, please tell again",fg='black',font={'times',11,'italic'},anchor='w')
                        y+=40
                        label11a.place(x=25,y=y)
                        label11a.pack(side='top')
                        self.sf.pack()
                        self.update()
                        self.pack(fill=BOTH,expand=True)
                        self.sf.yview('moveto', y)
                        self.engine.say('Sorry could not recognize your voice, please tell again')
                        self.engine.runAndWait()
                        label11a.after(2000, label11a.destroy())
                        pass
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                        label5=Label(self.inner_frame,text="Sorry  could not understand audio",fg='black',font={'times',11,'italic'},anchor='w')
                        y+=40
                        label5.place(x=25,y=y)
                        label5.pack(side='top')
                        self.sf.pack()
                        self.update()
                        self.sf.yview('moveto', y)

        if len(self.output)==0:
            error_condition()
        if self.exit_counter==0:
                label1c=Label(self.inner_frame,text="")
                label1c.pack()
                lable6=Label(self.inner_frame,text="Please confirm your symptoms by saying YES/NO",fg='Black',font={'Times New Roman',12,'bold'},anchor='w',justify=LEFT)
                y+=40
                lable6.place(x=0,y=y)
                lable6.pack(side='top')
                self.sf.pack()
                self.update()
                print("Please confirm your symptoms by saying YES/NO")
                self.engine.say('Please confirm your symptoms by saying YES or NO')
                self.engine.runAndWait()

                counter=0
                while True:
                    if self.output==[]:
                        break
                    else:
                        while True:
                            lable7=Label(self.inner_frame,text=self.output[0],fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                            lable7.place(x=25,y=self.y1)
                            lable7.pack(side='top')
                            self.y1=self.y1+40
                            self.sf.yview('moveto', self.y1)
                            print(self.output[0])
                            self.sf.pack()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            time.sleep(0.25)                   
                            self.engine.say(self.output[0])
                            self.engine.runAndWait()

                            counter+=1
                            with sr.Microphone() as source:
                                audio = self.recognizer.record(source,duration=3)
                                try:
                                    self.text2 = self.recognizer.recognize_google(audio)
                                    if difflib.get_close_matches(soundex(self.text2),[soundex("yes")]):
                                        self.symptoms.append(self.output[0])
                                        self.output.pop(0)
                                        if self.output==[]:
                                            break
                                    elif difflib.get_close_matches(soundex(self.text2),[soundex("no")]):
                                        self.output.pop(0)
                                        if self.output==[]:
                                            break
                                    else:
                                        if counter>5:
                                            break
                                        else:
                                            print("Sorry could not recognize your voice. Please tell again!")
                                            lable8=Label(self.inner_frame,text="Sorry could not recognize your voice. Please tell again!",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                                            lable8.place(x=25,y=self.y1)
                                            lable8.pack(side='top')
                                            self.sf.pack()
                                            self.update()
                                            self.pack(fill=BOTH,expand=True)
                                            self.sf.yview('moveto',self.y1)
                                            self.engine.say('Sorry could not recognize your voice. Please tell again')
                                            self.engine.runAndWait()
                                            lable8.after(1000, lable8.destroy())
                                except:
                                    print("Sorry could not recognize your voice")
                                    lable9=Label(self.inner_frame,text="Sorry could not recognize your voice!",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                                    lable9.place(x=25,y=self.y1)
                                    lable9.pack(side='top')
                                    self.sf.pack()
                                    self.update()
                                    self.sf.yview('moveto',self.y1)
                                    self.engine.say('Sorry could not recognize your voice')
                                    self.engine.runAndWait()
                                    lable9.after(1000, lable9.destroy())
                        break
        if len(self.symptoms)==0 and self.exit_counter==0:
            error_condition()
        #Appending the fever type to the symptoms list, if the temp is > 98 F
        if cond!="No fever":
            self.symptoms.append(cond)


    def display_symptoms(self):
        #self.symptoms=['obesity']

        if len(self.symptoms)>0:
            label1d=Label(self.inner_frame,text="")
            label1d.pack()
            lable13=Label(self.inner_frame,text="Recorded symptoms are:",fg='Black',font={'Times New Roman',12,'bold'},anchor='w')
            lable13.place(x=25,y=self.y1)
            lable13.pack(side='top')
            self.sf.yview('moveto',self.y1)
            self.sf.pack()
            self.sf.yview_moveto(99999)
            self.sf.update()
            self.update()
            self.sf.yview_moveto(99999)
            self.sf.update()
            self.update()
            time.sleep(0.25)
            self.engine.say("Recorded symptoms are")
            self.engine.runAndWait()
            y2=self.y1+25
            for i in self.symptoms:
                lable14=Label(self.inner_frame,text=i,fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                lable14.place(x=25,y=y2)
                lable14.pack(side='top')
                self.sf.pack()
                self.sf.yview_moveto(99999)
                self.sf.update()
                self.update()
                self.sf.yview_moveto(99999)
                self.sf.update()
                self.update()
                y2=y2+25
                time.sleep(0.25)
                self.engine.say(i)
                self.engine.runAndWait()
                self.y1+=y2
        else:
            print('bye')
            lable15=Label(self.inner_frame,text="Bye",fg='black',bg='white',width=30,font={'times',12,'bold'},anchor='w')
            lable15.place(x=25,y=self.y1)
            self.update()
            lable15.pack(side='top')
            self.sf.pack()
            self.sf.yview('moveto',self.y1)
            self.engine.say("bye")
            self.engine.runAndWait()
        

    def classify_symptoms(self):
        #self.symptoms=['cramps','swollen legs']
        df=pd.read_csv("Training_kag.csv")
        df_test=pd.read_csv("Testing_kag.csv")
        spl_quest=pd.read_csv("special_questions.csv",index_col=None)#header=None)
        df.columns=[i.replace('_',' ') for i in df_test.columns]
        df_test.columns=[i.replace('_',' ') for i in df_test.columns]
        self.le.fit(pd.concat([df['prognosis'], df_test['prognosis']]))
        self.le.fit_transform(df['prognosis'])
        self.model.fit(df[df.columns.difference(['prognosis'])], self.le.fit_transform(df['prognosis']))
        y_pred=self.model.predict(df_test[df_test.columns.difference(['prognosis'])])
        y_true = self.le.fit_transform(df_test['prognosis'])
        df_copy = df.iloc[0:1,:].copy() #pd.DataFrame().reindex_like(df)
        df_copy.append(pd.Series(), ignore_index=True)
        #print( df_copy.shape)
        symptoms = df.columns
        remedy=""

        for c in df_copy.columns:
            df_copy[c] = 0
        df_copy = df_copy[df_copy.columns.difference(['prognosis'])]
        calc=0

        lable27=Label(self.inner_frame,text="\n Please tell YES/NO if you have these symptoms:",fg='Black',font={'Times New Roman',12,'bold'})
        lable27.pack(side='top')                           
        self.pack(fill=BOTH,expand=True)
        self.sf.pack()
        self.sf.yview_moveto(99999)
        self.sf.update()
        self.update()
        self.sf.yview_moveto(99999)
        self.sf.update()
        self.update()
        time.sleep(0.25)
        print("Please tell YES/NO if you have these symptoms:")
        self.engine.say('Please tell YES or NO if you have these symptoms')
        self.engine.runAndWait()
        first_list=['fatigue','phlegm','chills','lethargy']
        s=0
        while (s==0):
             
            if len(first_list)==0:
                s=1
                break      
            lable27a=Label(self.inner_frame,text=first_list[0],fg='black',bg='white',font={'times',12,'bold'})
            lable27a.pack(side='top')
            self.y1=self.y1+40
            self.sf.yview('moveto', self.y1)
            print(first_list)
            self.sf.pack()
            self.sf.yview_moveto(99999)
            self.sf.update()
            self.update()
            self.sf.yview_moveto(99999)
            self.sf.update()
            self.update()
            time.sleep(0.25)                   
            self.engine.say(first_list[0])
            self.engine.runAndWait()
            while True:
                with sr.Microphone() as source:
                    audio = self.recognizer.record(source,duration=5)
                    count2=0
                    try:
                        self.inp=self.recognizer.recognize_google(audio)
                        break
                    except sr.UnknownValueError:
                        print("Sorry  could not understand your voice")
                        label19=Label(self.inner_frame,text="Sorry  could not recognize your voice",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                        label19.place(x=25,y=100)
                        label19.pack(side='top')                           
                        self.pack(fill=BOTH,expand=True)
                        self.sf.pack()
                        self.sf.yview_moveto(99999)
                        self.sf.update()
                        self.update()
                        self.sf.yview_moveto(99999)
                        self.sf.update()
                        self.update()
                        time.sleep(0.25)
                        self.engine.say('Sorry could not recognize your voice. Please tell yes or no again')
                        self.engine.runAndWait()
                        label19.after(1000, label19.destroy())
                        count2+=1
                        if count2>2:
                            break
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                        label20=Label(self.inner_frame,text="Sorry  could not understand audio",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                        label20.place(x=25,y=140)
                        label20.pack(side='top')
                        self.sf.pack()
                        self.update()
                        self.sf.yview('moveto', 140)
                        self.update()
                        count2+=1
                        if count2>2:
                            break
            if any([difflib.get_close_matches(soundex(self.inp),[soundex("no")]), self.inp.lower()=='no']):
                print("NO")
                self.engine.runAndWait()
                first_list.pop(0)
            elif any([difflib.get_close_matches(soundex(self.inp),[soundex("yes")]), self.inp.lower()=='yes']):
                print("YES")
                self.symptoms.append(first_list[0])
                first_list.pop(0)

        def df_create(df,sym_lis,sym_covered):
            for i in sym_lis:
                if i in symptoms:
                    sym_covered.append(i)
                    df_copy[i]=1
            return sym_covered,df_copy

        def disease_predict(model1,df1,le1):
            y_true = model1.predict_proba(df_copy)
            print(y_true)
            dis = []
            for i in range(len(y_true[0])):
                if y_true[0][i] >=0.1:
                    dis.append(i)
            i=np.argmax(y_true)
            if y_true[0][i]>=0.8:
                print(i)
                print(y_true[0][i])
                disname=[]
                disname= le1.inverse_transform([model1.classes_[i]])
                #return disname,y_true[0][i]
            else:
                print(dis)
                #for d in dis:
                    #if y_true[0][d] in y_lis:
                    #if y_true[0][d] >=0.1:
                disname = le1.inverse_transform(dis)
                print("Possible Diseases: >>> ", disname)
            return disname, y_true[0][i],dis
        
        def remaining_syms(model,df,disease,symptoms_covered):
            df_fil = df[df['prognosis'].isin(disease)]
            df_fil = df_fil.loc[:, (df_fil != 0).any(axis=0)]
            df_fil = df_fil[df_fil.columns.difference(['prognosis'])]
            d=df_fil.columns.to_list()
            
            #If no fever, remove high and mild fever from the symptoms list
            if cond=="No fever":
                if "high fever" in d:
                    d.remove("high fever")
                if "mild fever" in d:
                    d.remove("mild fever")
            elif cond=="high fever":
                if "mild fever" in d:
                    d.remove("mild fever")
            elif cond=="mild fever":
                if "high fever" in d:
                    d.remove("high fever")
            diff= np.setdiff1d(['fatigue','phlegm','chills','lethargy'],self.symptoms)
            if len(diff)>0:
                for i in diff:
                    if i in d:
                        d.remove(i) 
            print(d)    
            counter=0
            for i in symptoms_covered:
                if i in d:
                    d.remove(i)
            print("Remaining symptoms: ", d)
            
            gap=Label(self.inner_frame,text="",fg='black',font={'times',12,'bold'},anchor='w')
            gap.place(x=25,y=self.y1)
            gap.pack()           
            self.sf.pack()
            self.sf.yview_moveto(99999)
            self.sf.update()
            self.update()
            self.sf.yview_moveto(99999)
            self.sf.update()
            self.update()
            time.sleep(0.25)
            
            if counter==0:
                row=1
                i=0
                while i<len(d):
                    x=0
                    try:
                        if len(d[i+3])<15:
                            lable17=Label(self.inner_frame,text=" {}  | {} | {} | {} ".format(d[i],d[i+1],d[i+2],d[i+3]),fg='black',bg='white',relief='raised',font={'times',12,'bold'})
                            lable17.pack()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            time.sleep(0.25)
                            
                        else:
                            lable17=Label(self.inner_frame,text=" {} | {} | {} ".format(d[i],d[i+1],d[i+2]),fg='black',bg='white',relief='raised',font={'times',12,'bold'})
                            lable17.pack()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            time.sleep(0.25)
                            x=1
                    except Exception as e:
                        print(e)                        
                        if i+1==len(d):
                            lable17c=Label(self.inner_frame,text=" {}  ".format(d[i]),fg='black',bg='white',relief='raised',font={'times',12,'bold'})
                            lable17c.pack()
                        elif i+2==len(d):
                            lable17c=Label(self.inner_frame,text=" {} | {} ".format(d[i],d[i+1]),fg='black',bg='white',relief='raised',font={'times',12,'bold'})
                            lable17c.pack()
                        elif i+3==len(d):
                            lable17c=Label(self.inner_frame,text=" {} | {} | {} ".format(d[i],d[i+1],d[i+2]),fg='black',bg='white',relief='raised',font={'times',12,'bold'})
                            lable17c.pack()
                        else:
                            pass
                        self.sf.pack()
                        self.sf.yview_moveto(99999)
                        self.sf.update()
                        self.update()
                        self.sf.yview_moveto(99999)
                        self.sf.update()
                        self.update()
                        time.sleep(0.25)  
                    if x==0:
                        i+=4
                    else:
                        i+=3                
            
            lis=[]
            state=0
            while(state<4):
                while True:
                    gap1=Label(self.inner_frame,text="",fg='black',font={'times',12,'bold'},anchor='w')
                    gap1.place(x=25,y=self.y1)
                    gap1.pack()
                    self.sf.pack()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    time.sleep(0.25)
                   
                    print("Pick any of the symptoms")
                    lable18=Label(self.inner_frame,text="Pick any of the mentioned symptoms that you might be facing, if not tell 'No'" ,fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                    lable18.place(x=25,y=self.y1)
                    lable18.pack(side='top')
                    self.sf.pack()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    time.sleep(0.25)
                    self.engine.say("Pick any of the mentioned symptoms that you might be facing, if not tell 'No'")
                    self.engine.runAndWait()
                    with sr.Microphone() as source:
                        audio = self.recognizer.record(source,duration=7)
                        count1=0
                        try:
                            self.inp=self.recognizer.recognize_google(audio)
                            print( difflib.get_close_matches(soundex(self.inp),[soundex("no"),soundex("yes")]))
                            break
                        except sr.UnknownValueError:
                            print("Sorry  could not understand your voice")
                            label19=Label(self.inner_frame,text="Sorry  could not recognize your voice",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                            label19.place(x=25,y=100)
                            label19.pack(side='top')                           
                            self.pack(fill=BOTH,expand=True)
                            self.sf.pack()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            time.sleep(0.25)
                            self.engine.say('Sorry could not recognize your voice')
                            self.engine.runAndWait()
                            label19.after(1000, label19.destroy())
                            count1+=1
                            if count1>2:
                                break
                        except sr.RequestError as e:
                            print("Could not request results from Google Speech Recognition service; {0}".format(e))
                            label20=Label(self.inner_frame,text="Sorry  could not understand audio",fg='black',bg='white',font={'times',11,'italic'},anchor='w')
                            label20.place(x=25,y=140)
                            label20.pack(side='top')
                            self.sf.pack()
                            self.update()
                            self.sf.yview('moveto', 140)
                            self.update()
                            count1+=1
                            if count1>2:
                                break
                matched_symp=''
                if difflib.get_close_matches(metaphone("no"),[metaphone(self.inp)]):
                    if metaphone("no")[0]==metaphone(self.inp)[0]:
                        if metaphone(self.inp) == 'NS':
                            matched_symp='nausea'
                        elif fuzz.partial_ratio(soundex(self.inp),soundex("nausea")) > 80:
                            matched_symp='nausea'                       
                        else:
                            state+=1
                            lable18a=Label(self.inner_frame,text="No",fg='black',bg='light blue',relief='raised',font={'times',12,'bold'},anchor='w')
                            #lable18a.place(x=25,y=self.y1)
                            self.update()
                            lable18a.pack(side='top')  
                            self.sf.pack()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            time.sleep(0.25)                           
                            self.engine.say(self.inp)
                            self.engine.runAndWait()
                            break
                else:                 
                    match_index = 0
                    matched_symp = ""
                    for item in d:
                        if fuzz.partial_ratio(item, self.inp) > 70:
                            this_match = fuzz.ratio(item, self.inp) + fuzz.partial_ratio(item, self.inp) + fuzz.token_sort_ratio(item, (self.inp).replace(' ', ''))
                            if this_match > match_index:
                                match_index = this_match
                                matched_symp = item
                
                if matched_symp is "":
                    if difflib.get_close_matches(metaphone(self.inp) , ['MLS','ML','MLX']) and 'malaise' in d:
                        #if 0<=abs(int(soundex (self.inp)[1:])-int(soundex('malaise')[1:]))<=50:
                    #elif difflib.get_close_matches(metaphone(self.inp),['MLS']):
                        matched_symp='malaise'
                    elif difflib.get_close_matches(metaphone(self.inp) , ['SWTNK']) and 'sweating' in d:
                        matched_symp='sweating'
                    
                if matched_symp is not '':
                    print(matched_symp)
                    lable18b=Label(self.inner_frame,text=matched_symp,fg='black',bg='light blue',relief='raised',font={'times',12,'bold'},anchor='w')
                   # lable18b.place(x=25,y=self.y1)
                    self.update()
                    lable18b.pack(side='top')
                    self.sf.pack()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    time.sleep(0.25)
                    self.engine.say(matched_symp)
                    self.engine.runAndWait()
                    lis.append(matched_symp)
                    lis=list(set(lis))
                    print(lis)
            return lis
        
        def uni_quest(result_list):
            quest=""
            res=-1
            for n in result_list: 
                state=0       
                while (state==0):
                    print(n)              
                    quest=spl_quest.iloc[n,3]
                    print(quest)
                    gap2=Label(self.inner_frame,text="",fg='black',font={'times',12,'bold'},anchor='w')
                   # gap2.place(x=25,y=self.y1)
                    gap2.pack(side='top')
                    self.sf.pack()
                    self.update()
                    self.sf.update()
                    self.sf.yview('moveto',self.y1)
                    time.sleep(1)
                        
                    sq=Label(self.inner_frame,text=quest,wraplength=500,fg='black',bg='white',font={'times',12,'bold'})
                   # sq.place(x=25,y=self.y1)
                    self.update()
                    sq.pack(side='top')
                    self.sf.pack()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    time.sleep(0.25)
                    self.engine.say(quest)
                    self.engine.runAndWait()
                    with sr.Microphone() as source:
                        audio = self.recognizer.record(source,duration=3)
                        try:
                            self.text2=self.recognizer.recognize_google(audio)
                            if difflib.get_close_matches(soundex(self.text2),[soundex("yes")]):
                                ans=Label(self.inner_frame,text="Yes",fg='black',bg='light blue',relief='raised',font={'times',12,'bold'},anchor='w')
                               # ans.place(x=25,y=self.y1)
                                self.update()
                                ans.pack(side='top')
                                self.sf.pack()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                time.sleep(0.25)
                                self.engine.say("Yes")
                                self.engine.runAndWait()
                                res=n
                                break                  
                                
                            elif difflib.get_close_matches(soundex(self.text2),[soundex("no")]):
                                ans=Label(self.inner_frame,text="No",fg='black',bg='light blue',relief='raised',font={'times',12,'bold'},anchor='w')
                               # ans.place(x=25,y=self.y1)
                                self.update()
                                ans.pack(side='top')
                                self.sf.pack()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                time.sleep(0.25)
                                self.engine.say("No")
                                self.engine.runAndWait()
                                state=1 
                                
                            else:
                                print("Sorry could not recognize your voice. Please tell again!")
                                lable8a=Label(self.inner_frame,width=70,text="Sorry could not recognize your voice. Please tell again!",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                                lable8a.place(x=25,y=self.y1)
                                lable8a.pack(side='top')
                                self.pack(fill=BOTH,expand=True)
                                self.sf.pack()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                time.sleep(0.25)
                                self.engine.say('Sorry could not recognize your voice. Please tell again')
                                self.engine.runAndWait()
                                lable8a.after(1000, lable8a.destroy()) 
                                continue
                        except:
                            print("Sorry could not recognize your voice")
                            lable9a=Label(self.inner_frame,text="Sorry could not recognize your voice!",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                            lable9a.place(x=25,y=self.y1)
                            lable9a.pack(side='top')
                            self.sf.pack()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            self.sf.yview_moveto(99999)
                            self.sf.update()
                            self.update()
                            time.sleep(0.25)
                            self.sf.yview('moveto',self.y1)
                            self.engine.say('Sorry could not recognize your voice')
                            self.engine.runAndWait()
                            lable9a.after(1000, lable9a.destroy())
                            continue
                if res== n:
                    remedy=spl_quest.iloc[n,4]
                    return res,remedy
                else: 
                    remedy="" 
            return res,remedy    
         
        symptoms_covered=[]
        symptoms_covered,df_copy=df_create(df_copy,self.symptoms,symptoms_covered)
        print("Symptoms covered are : ",symptoms_covered)

        (res,prob,num_rep)=disease_predict(self.model,df_copy,self.le)
        print("res is",res)

        while(prob>0.1):
            if prob<=0.75 and calc<4:
                calc+=1
                ext_syms=remaining_syms(self.model,df,res,symptoms_covered)
                symptoms_covered,df_copy=df_create(df_copy,ext_syms,symptoms_covered)
                print("Symptoms covered are : ",symptoms_covered)
                (res,prob,num_rep)=disease_predict(self.model,df_copy,self.le)
            else:
                if len(res)>1:
                    (num_rep,remedy)=uni_quest(num_rep)
                    if num_rep!=-1:
                        res=self.le.inverse_transform([self.model.classes_[num_rep]])
                if remedy=="" and len(res)==1:
                    remedy=spl_quest.iloc[spl_quest[spl_quest['Disease']==res[0]].index.item(),4]
                    
                elif all([remedy=="", len(res)>1]):
                    print("Sorry could not predict any disease! Would you want to start over?")   
                    lable26=Label(self.inner_frame,text="\n Sorry could not predict any disease! Would you want to start over?",fg='black',font={'times',12,'bold'},anchor='w')
                    self.update()
                    lable26.pack(side='top')
                    self.sf.pack()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    time.sleep(0.25)
                    self.engine.say("Sorry could not predict any disease! Would you want to start over? Please tell YES or NO")
                    self.engine.runAndWait() 
                    state=0
                    while state<3:
                        with sr.Microphone() as source:
                            audio = self.recognizer.record(source,duration=5)
                            try:
                                self.text1=self.recognizer.recognize_google(audio)
                                if self.text1.lower()=='yes':
                                    self.quit()
                                    main()
                                elif self.text1.lower()=='no':
                                    print("Bye")
                                    label12=Label(self.inner_frame,text="Bye!",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                                    label12.pack(side='top')
                                    self.sf.pack()
                                    self.sf.yview_moveto(99999)
                                    self.sf.update()
                                    self.update()
                                    self.sf.yview_moveto(99999)
                                    self.sf.update()
                                    self.update()
                                    time.sleep(0.25)
                                    self.engine.say("Bye")
                                    self.engine.runAndWait()
                                    time.sleep(2)
                                    exit()
                                else:
                                    state+=1  
                                    if state == 3:
                                        exit()                           
                            except sr.UnknownValueError:
                                print("Sorry  could not understand your voice")
                                label11a=Label(self.inner_frame,text="Sorry  could not recognize your voice, please tell again",fg='black',font={'times',11,'italic'},anchor='w')
                                self.sf.pack()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                self.sf.yview_moveto(99999)
                                self.sf.update()
                                self.update()
                                time.sleep(0.25)
                                self.engine.say('Sorry could not recognize your voice, please tell again')
                                self.engine.runAndWait()
                                label11a.after(2000, label11a.destroy())
                                pass
                            except sr.RequestError as e:
                                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                                label5=Label(self.inner_frame,text="Sorry  could not understand audio",fg='black',font={'times',11,'italic'},anchor='w')
                                y+=40
                                label5.place(x=25,y=y)
                                label5.pack(side='top')
                                self.sf.pack()
                                self.update()
                                self.sf.yview('moveto', y)
                print("Suspected disease is : ", res)  
                gap3=Label(self.inner_frame,text="",fg='black',font={'times',12,'bold'},anchor='w')
                gap3.place(x=25,y=self.y1)
                gap3.pack(side='top')
                self.sf.pack()
                self.sf.yview_moveto(99999)
                self.sf.update()
                self.update()
                self.sf.yview_moveto(99999)
                self.sf.update()
                self.update()
                time.sleep(0.25)
                time.sleep(1)
                
                
                
                lable21=Label(self.inner_frame,text="The suspected disease is",fg='black',bg='white',font={'times',12,'bold'},anchor='w')
                lable21.place(x=25,y=self.y1)
                self.update()
                lable21.pack(side='top')
                self.sf.pack()
                self.sf.yview_moveto(99999)
                self.sf.update()
                self.update()
                self.sf.yview_moveto(99999)
                self.sf.update()
                self.update()
                time.sleep(0.25)
                self.engine.say("The suspected disease is")
                self.engine.runAndWait()
                for k in res:
                    lable21=Label(self.inner_frame,text=k,fg='black',bg='light blue',relief='solid',font={'times',12,'bold'},anchor='w')
                    lable21.place(x=25,y=self.y1)
                    self.sf.update()
                    lable21.pack(side='top')
                    self.sf.pack()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    self.sf.yview_moveto(99999)
                    self.sf.update()
                    self.update()
                    time.sleep(0.25)
                    self.engine.say(k)
                    self.engine.runAndWait()
                    
                    if remedy is not "":                
                        print(remedy)
                        lable25=Label(self.inner_frame,text="The remedy for {} is: {} ".format(k,remedy),wraplength = 500,fg='black',bg='white',font={'times',12,'bold'})
                        lable25.place(x=25,y=self.y1)
                        self.sf.update()
                        lable25.pack(side='top')
                        self.sf.pack()
                        self.sf.yview_moveto(99999)
                        self.sf.update()
                        self.update()
                        self.sf.yview_moveto(99999)
                        self.sf.update()
                        self.update()
                        time.sleep(0.25)
                        self.engine.say("The remedy for {} is:".format(k))
                        self.engine.say(remedy)
                        self.engine.runAndWait()
                   
                    gap21a=Label(self.inner_frame,text="\n ")
                    self.sf.update()
                    gap21a.pack(side='top')
                    self.sf.pack()
                    self.sf.yview('moveto',self.y1)
                    self.update()
                    gap21b=Label(self.inner_frame,text=" ")
                    gap21b.pack(side='top')
                    self.sf.yview('moveto',self.y1)
                    
                    
                    self.data['Symptoms']=symptoms_covered
                    self.data['Disease']=res[0]
                    whattime = datetime.datetime.now()
                    self.data['Time']=whattime
                    print(self.data)
                    fb= firebase.FirebaseApplication("https://ihb-3fc83.firebaseio.com/", None)
                    result1= fb.post("/ihb-3fc83:/Patient Data", self.data)

                print("Symptoms covered are : ",symptoms_covered)
                break


def main():
    

    root=Tk()
    root.geometry("800x500")
    app=SymptomRecognizer(root)
    app.pack(side="top", fill="both", expand=True)
    root.after(2000,root.destroy())
    root.mainloop()


if __name__ == '__main__':
    main_counter=0
    main()

