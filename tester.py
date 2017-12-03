from urllib import request,response
import json

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
