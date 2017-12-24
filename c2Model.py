import nltk
import collections
import re
import sklearn as sk
#import tensorflow
#from tensorflow import tflearn
class c2Model():

    file=''
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
            bag=collections.defaultdict(lambda:0 )
            sents=self.char_sent_dic[character]
            for sent in sents:
                sent=re.sub(r'[\n,.!?\\\"\']','',sent).lower()
                for word in sent.split(' '):
                    bag[word]+=1

            return bag
        else:
            print('create char dic first')
            return None

waifu=c2Model('CodeGeassCorpus.txt')
char_dic=waifu.get_char_dic()
print(char_dic)
print(len(char_dic['C.C.']))
print (waifu.char_bag('Lelouch'))

