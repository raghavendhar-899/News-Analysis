# Import necessary libraries
import torch
from transformers import pipeline, AutoTokenizer

# import pathlib
# import textwrap

from google import generativeai as genai

# from IPython.display import display
# from IPython.display import Markdown

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY_SCORE'))

model = genai.GenerativeModel(model_name='gemini-1.5-flash')

# Define the function to generate a summary of the provided text
def get_summary(text):
    """
    Generates a summary of the provided text using the BART summarization model.

    Args:
        text (str): The text to be summarized.

    Returns:
        str: The summarized text.
    """
    # print('inside')
    # Load the BART summarization model
    summarizer = pipeline("summarization",model='sshleifer/distilbart-cnn-12-6')

    # tokenizer = AutoTokenizer.from_pretrained("valhalla/bart-large-finetuned-squadv1")

    # text = tokenizer(text, padding=1000, truncation=True)

    # Generate the summary
    summary = summarizer(text[:1000], max_length=60, min_length=20, do_sample=False)[0]["summary_text"]

    # print(summary,'summary')

    return summary


# def to_markdown(text):
#   text = text.replace('•', '  *')
#   return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def get_score(text = "no artical found return 0",company = 'no company return 0'):
#    base_query=f'Please just answer either true or false it the following artical heading effect stock price of {company}.\n'
   query = f"""
   Identify the sentiment towards the {company} stocks of the news article from -10 to +10 where -10 being the most negative and +10 being the most positve , and 0 being neutral

   GIVE ANSWER IN ONLY ONE WORD AND THAT SHOULD BE THE SCORE

   Article : {text}
   """

   print(query[:10])

   response = model.generate_content(query)
   try:
    score = int(response.text)
   except:
      print('error score')
      return 0
   return score



#Test
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_summary(text))

    