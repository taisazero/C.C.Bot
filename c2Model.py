import nltk
import collections
import re
import pandas as pd
from nltk.corpus import stopwords
import sklearn as sk
import tensorflow as tf
from textblob import TextBlob

#ToDo:
"""
- Clean up data text file and look into C.C. logs
- implement a TF model and start chatbot
- Make a classifier classifies user sentence as a character
- Add functionalities to chatbot
- Install AWS repo


After that:
 Separate class
- Work on speech to text
- Make bot join a voice channel
- listen to speakers
-generate mp3 file of speech
-send to google speech api
-generate a text file
"""
class c2Model():

    file=''
#hi
    eng_stops=set(stopwords.words('english'))
    char_sent_dic= collections.defaultdict(lambda :[])
    def __init__(self,f):
        self.file=f



    def get_char_dic(self):
        reader=open(self.file,'r',encoding='utf-8')
        speaker='narrator'
        sentence=''
        for line in reader.readlines():
            if(line=='THE END'):
                speaker='narrator'
            sentence=str(line)
            sentence=re.sub(r'\n','',sentence)

            if(line.__contains__(':')):
                speaker=line.split(':')[0]
                speaker= re.sub(r' ','',speaker)
                sentence=str(line.split(';')[1:len(line.split(':'))])
            if(sentence!='[]'):
                self.char_sent_dic[speaker].append(sentence)
        return self.char_sent_dic
    def char_bag(self,character):
        if(len(self.char_sent_dic.keys())>0):
            bag=collections.defaultdict(lambda:['',0])
            sents=self.char_sent_dic[character]
            for sent in sents:
                sent=re.sub(r'[\n,.!?\\\"\']','',sent).lower()
                if(len(sent.split(' '))>0):
                    tagged =nltk.pos_tag(sent.split())
                    for word, tag in tagged:
                        if(word not in self.eng_stops and word !='' and word !=' '):
                            if (tag=='NN' or tag=='NNP' or tag=='VB' or tag=='RB'or tag=='NNS'or tag=='JJ'or 'FW'):
                                bag[word][0]=tag
                                bag[word][1]+= 1


            return bag
        else:
            print('create char dic first')
            return None
    def bag_csv(self,filename,character):
        bag=self.char_bag(character)
        print(bag.items())
        my_panda=pd.DataFrame.from_dict(bag,orient='index')
        print(my_panda)
        my_panda.to_csv(filename,encoding='utf-8')
    def sentiment(self,character):
       sents= self.get_char_dic()[character]
       total=''
       for sent in sents:
           total+=' ' +sent
       t=TextBlob(total)
       print(character,t.sentiment)






waifu=c2Model('CodeGeassCorpus.txt')
for key in waifu.get_char_dic().keys():
    #waifu.bag_csv('bags\\'+key+'.csv',key)
    waifu.sentiment(key)

