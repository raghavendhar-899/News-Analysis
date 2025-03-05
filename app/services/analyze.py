# Import necessary libraries
import torch
from transformers import pipeline, AutoTokenizer
from datetime import datetime


import requests

import ollama

import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')




try:
    summarizer = pipeline("summarization",model='sshleifer/distilbart-cnn-12-6', device="mps")
except:
    print('Network Error')

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

    # ------------------ Hugging Face API -------------------
    summary = 'Unable to summarize...'
    try: 
        summary = summarizer(text[:1000], max_length=60, min_length=20, do_sample=False)[0]["summary_text"]

        print(summary[1:8])
        if summary[1:8]=="CNN.com":
            return "Unable to summarize..."
    except  Exception as e:
        print(e)
        print('Summerizer Failed to load')

    return summary

    # ------------------ Ollama API -------------------

    # query = f"""
    # Summarize the following article into 30 words or less:
    # {text}
    # """

    # response = ollama.chat(model=OLLAMA_MODEL, messages=[
    # {
    #     'role': 'user',
    #     'content': query,
    # },
    # ])

    # print('response',response)
    # summary = response['message']['content']
    # return summary


def get_score(title='No title return 0',text = "no artical found return 0",company = 'no company return 0',isnew=False):

    query = f"""
   Identify the sentiment towards the {company} stocks of the news article from -10 to +10 where -10 being the most negative and +10 being the most positve , and 0 being neutral

   GIVE ANSWER IN ONLY ONE NUMBER AND THAT SHOULD BE THE SCORE

   Article Title : {title}

   Article : {text}
   """
  
    #   ------------------ Google gemini api -------------------
    
    #    if isnew:
    #     GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY_SCORE_N')
    #    else:
    #     # Get the current datetime
    #     now = datetime.now()

    #     # Extract the hour in 24-hour format
    #     current_hour = now.hour
    
    #     GOOGLE_API_KEY=os.getenv(f'GOOGLE_API_KEY_SCORE_{current_hour}')

    #    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}'
    #    headers = {
    #     'Content-Type': 'application/json'
    #     }


    
    #    data = {
    #          "contents": [{
    #         "parts":[{
    #           "text": query}]}]
    #       }
    #    try:
    #     response = requests.post(url, headers=headers, json=data)
    #     json_response = response.json()
    #    except:
    #      print('Limit reched')
    #      score = 0
    #    try:
    #     score = int(json_response["candidates"][0]["content"]["parts"][0]["text"])
    #    except:
    #       print('error score')
    #       return 0
    #    return score


    #  ------------------ Ollama api -------------------
    response = ollama.chat(model=OLLAMA_MODEL, messages=[
    {
        'role': 'user',
        'content': query,
    },
    ])
    print('response',response)
    try:
        score = int(response['message']['content'])
    except:
        print('error score')
        return 0
    return score





#Test summary
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_summary(text))

#Test score
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_score('Infosys bags contract',text,'Infosys',True))


    