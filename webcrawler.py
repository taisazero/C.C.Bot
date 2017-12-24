from urllib import request,response
import json
import collections
from bs4 import BeautifulSoup
import re
import nltk


def get_links():
    list=[]
    url1='http://animetranscripts.wikispaces.com/Code+Geass%EF%BC%9A+Lelouch+of+the+Rebellion+-+%E3%82%B3%E3%83%BC%E3%83%89%E3%82%AE%E3%82%A2%E3%82%B9+%E5%8F%8D%E9%80%86%E3%81%AE%E3%83%AB%E3%83%AB%E3%83%BC%E3%82%B7%E3%83%A5'
    url2='http://animetranscripts.wikispaces.com/Code+Geass%EF%BC%9A+Lelouch+of+the+Rebellion+R2+-+%E3%82%B3%E3%83%BC%E3%83%89%E3%82%AE%E3%82%A2%E3%82%B9+%E5%8F%8D%E9%80%86%E3%81%AE%E3%83%AB%E3%83%AB%E3%83%BC%E3%82%B7%E3%83%A5+R2'
    my_r=request.urlopen(url1)
    r1=my_r.read()
    b1=BeautifulSoup(r1)
    my_r2=request.urlopen(url2)
    r2=my_r2.read()
    b2=BeautifulSoup(r2)
    for link in b1.find_all(attrs={'class':'wiki_link'}):
        if('Code+Geass'in link['href']):
            list.append('http://animetranscripts.wikispaces.com'+link['href'])
    for link in b2.find_all(attrs={'class':'wiki_link'}):
        if ('Code+Geass' in link['href']):
            list.append('http://animetranscripts.wikispaces.com' + link['href'])
    print(list)
    return list

def get_pizza_gifs():
    url='https://api.giphy.com/v1/gifs/search?api_key=DYaEYDVMv0FfGTMrkuR0ygQVc66rbwJ9&q=code%20geass%20pizza&limit=25&offset=0&rating=G&lang=en'
    response=request.urlopen(url)
    result=response.read()
    print(result)

    d=json.loads(result)
    list=[]
    for i in range(0,len(d['data'])):
        if (('cc' in d['data'][i]['slug'] and 'pizza' in d['data'][i]['slug'])or 'pizza' in d['data'][i]['title'] and 'cc' in d['data'][i]['title']):
            list.append(d['data'][i]['embed_url'])
    print (list)
    print(len(list))
    return list

class webcrawler():
    href=''
    mylist=[]
    lookFor=''
    lookFor2=''
    dic=collections.defaultdict(lambda :[])
    def __init__(self,link,p1,p2):
        self.href=link
        self.lookFor = p1
        self.lookFor2 = p2
    def __init__(self,list,p1,p2):
        self.mylist=list
        self.lookFor = p1
        self.lookFor2 = p2


    def read(self):
        lmao=''
        if (len(self.mylist)>0):
            for e in self.mylist:
                print(e)
                response= request.urlopen(e)
                result=response.read()
                bs=BeautifulSoup(result)
                lmao += str(bs.find(attrs={self.lookFor:self.lookFor2}))
                lmao= re.sub(r'[</]+[\w =\",:;#]+[>/]*','',lmao)
            sentences = nltk.sent_tokenize(lmao)
            print(sentences)
            return sentences


        else:

            response = request.urlopen(self.href)
            result = response.read()
            bs = BeautifulSoup(result)
            lmao = str(bs.find(attrs={self.lookFor: self.lookFor2}))
            lmao = re.sub(r'[</]+[\w =\",:;#]+[>/]*', '', lmao)
            sentences = nltk.sent_tokenize(lmao)
            print(sentences)
        return sentences



    def generate_txt(self,file,corpus):
           f=open(file,'w',encoding='utf-8')
           for sentence in corpus:
               for word in sentence.split(' '):
                   if(word != '\n'):
                    f.write(word+' ')
               if(word !='C.C.' and word!='V.V.'):
                    f.write('\n')

           f.close()

linkerinos=get_links()
print(linkerinos)
w=webcrawler(linkerinos,'class','wiki wikiPage')
my_corpus=w.read()
w.generate_txt('CodeGeassCorpus.txt',my_corpus)




