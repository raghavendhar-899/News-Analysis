import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY_VERIFY'))

model = genai.GenerativeModel(model_name='gemini-1.5-flash')


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))



def stockify(list, company):
    '''
    list: list of article headings
    
    Based on the headings this function will determine if it is corporate related news or not.

    By using gemini api
    '''
    stockified_articals=[]
    base_query=f'Please just answer either true or false it the following artical heading effect stock price of {company}.\n'
    for i in list:
      query=base_query+i[0]
      print('query:\n',query)
      response = model.generate_content(query)
      result = True if response.text[0]=='T' else False
      stockified_articals.append(i)
      print("result:\n", result)
    return stockified_articals


#Test
# list=['Amazon is having a secret sale on the Apple iPad 10th Gen that makes it cheaper than ever']
# print(stockify(list,"Apple"))


