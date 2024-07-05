# Import necessary libraries
import torch
from transformers import pipeline, AutoTokenizer
from datetime import datetime


import requests

import os
from dotenv import load_dotenv

load_dotenv()

summarizer = pipeline("summarization",model='sshleifer/distilbart-cnn-12-6')

# Define the function to generate a summary of the provided text
def get_summary(text):
    """
    Generates a summary of the provided text using the BART summarization model.

    Args:
        text (str): The text to be summarized.

    Returns:
        str: The summarized text.
    """

    # Generate the summary
    summary = summarizer(text[:1000], max_length=60, min_length=20, do_sample=False)[0]["summary_text"]

    print(summary[1:8])
    if summary[1:8]=="CNN.com":
       return "Unable to summarize..."

    return summary


def get_score(text = "no artical found return 0",company = 'no company return 0',isnew=False):
   
   if isnew:
    GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY_SCORE_N')
   else:
    # Get the current datetime
    now = datetime.now()

    # Extract the hour in 24-hour format
    current_hour = now.hour
   
    GOOGLE_API_KEY=os.getenv(f'GOOGLE_API_KEY_SCORE_{current_hour}')
   
   query = f"""
   Identify the sentiment towards the {company} stocks of the news article from -10 to +10 where -10 being the most negative and +10 being the most positve , and 0 being neutral

   GIVE ANSWER IN ONLY ONE WORD AND THAT SHOULD BE THE SCORE

   Article : {text}
   """
   url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}'
   headers = {
    'Content-Type': 'application/json'
    }
   
   data = {
         "contents": [{
        "parts":[{
          "text": query}]}]
      }
   try:
    response = requests.post(url, headers=headers, json=data)
    json_response = response.json()
   except:
     print('Limit reched')
     score = 0
   try:
    score = int(json_response["candidates"][0]["content"]["parts"][0]["text"])
   except:
      print('error score')
      return 0
   return score



#Test
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_summary(text))

    