import requests

import os
from dotenv import load_dotenv

# import concurrent.futures

load_dotenv()



def stockify(list, company):
    '''
    list: list of article headings
    
    Based on the headings this function will determine if it is corporate related news or not.

    By using gemini api
    '''
    GOOGLE_API_KEY_VERIFY1=os.getenv('GOOGLE_API_KEY_VERIFY1')
    GOOGLE_API_KEY_VERIFY2=os.getenv('GOOGLE_API_KEY_VERIFY2')
    stockified_articles=[]
    base_query=f'Please just answer either true or false it the following artical heading effect stock price of {company}.\n'
    t=0
    url1 = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY_VERIFY1}'
    url2 = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY_VERIFY2}'
    headers = {
    'Content-Type': 'application/json'
    }
    for i in list:
      t+=1
      print(t)
      if t>=30 or len(stockified_articles)>=15:
         break
      if t<15:
         url=url1
      elif t<30:
         url=url2
      query=base_query+i[0]
      print('query:\n',query)
      data = {
         "contents": [{
        "parts":[{
          "text": query}]}]
      }
      result=False
      try:
        # response = verify_model.generate_content(query)
        response = requests.post(url, headers=headers, json=data)
        json_response = response.json()
        result = True if json_response["candidates"][0]["content"]["parts"][0]["text"][0]=='T' else False
        if result:
          stockified_articles.append(i)
      except:
         print('Limit Exceeded')
      print("result:\n", result)
    return stockified_articles


#Test
# list=['Amazon is having a secret sale on the Apple iPad 10th Gen that makes it cheaper than ever']
# print(stockify(list,"Apple"))


