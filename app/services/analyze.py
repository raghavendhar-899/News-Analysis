# Import necessary libraries
import torch
from transformers import pipeline, AutoTokenizer
from datetime import datetime


import requests

import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
from app.utils.logger import get_logger
from app.utils.ollama_retry import chat_with_reset_retry

logger = get_logger(__name__)
logger.info('Ollama model = %s', OLLAMA_MODEL)




# try:
#     summarizer = pipeline("summarization",model='sshleifer/distilbart-cnn-12-6', device="mps")
# except:
#     print('Network Error')

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
    # summary = 'Unable to summarize...'
    # try: 
    #     summary = summarizer(text[:1000], max_length=60, min_length=20, do_sample=False)[0]["summary_text"]

    #     print(summary[1:8])
    #     if summary[1:8]=="CNN.com":
    #         return "Unable to summarize..."
    # except  Exception as e:
    #     print(e)
    #     print('Summerizer Failed to load')

    # return summary

    # ------------------ Ollama API -------------------

    # query = f"""
    # Summarize the following article with in 30 words or less:
    # {text}
    # """

    query = f"""
    ### ROLE
    You are a Senior Financial News Editor at a global wire service. You specialize in "High-Density Data Extraction," converting complex financial reports into actionable, one-sentence "News Flashes" for institutional traders.

    ### OBJECTIVE
    Condense the article into a high-signal financial summary. Your goal is to convey the "Market Delta" (the change or surprise).

    ### CONSTRAINTS
    1. **Word Count:** Strict maximum of 30 words. 
    2. **No Meta-Discourse:** Do not start with "This article is about," "The author mentions," or "In this text." Start directly with the subject.
    3. **Active Voice:** Use strong verbs and active voice to save space and increase impact.
    4. **No Lists:** Provide the summary as a single, cohesive prose sentence or two short sentences.

    ### EVALUATION CRITERIA
    - **Completeness:** Does it capture the main entity and the primary action?
    - **Conciseness:** Is every word pulling its weight?
    - **Clarity:** Is it readable at a glance?

    ### INPUT DATA
    Text: {text}

    ### FINAL OUTPUT
    Just the 30-word summary. Don't give any explanation or commentary.
    """

    response = chat_with_reset_retry(
        OLLAMA_MODEL,
        messages=[
            {
                'role': 'user',
                'content': query,
            },
        ],
        service_name='summary',
    )
    logger.debug('ollama response: %s', response)
    summary = response['message']['content']
    return summary


def get_score(title='No title return 0',text = "no artical found return 0",company = 'no company return 0',isnew=False):
    logger.debug('Get_score called for company=%s title=%s', company, title)
#     query = f"""
#     For the following news article about {company}, assign a sentiment score toward its stock on a scale from -10 to +10. Use -10 for extremely negative sentiment, 0 for neutral, and +10 for extremely positive sentiment. Analyze the content carefully and respond with only a single numerical score (do not include any text or explanation).

#     Article Title: {title}

#     Article Text: {text}

#    """

    query = f"""
    ### ROLE
    You are a Senior Quantitative Equity Analyst specializing in Natural Language Processing (NLP). Your objective is to extract high-signal financial sentiment from news data to predict short-term stock price momentum for a specific ticker.

    ### EVALUATION RUBRIC
    Assign a sentiment score from -10 to +10 based on the following scale:
    - **-10 to -8 (Severe):** Existential threats (e.g., bankruptcy, major fraud, massive earnings miss, severe regulatory litigation).
    - **-7 to -3 (Negative):** Negative catalysts (e.g., analyst downgrades, minor earnings miss, product delays, loss of market share).
    - **-2 to +2 (Neutral):** Noise or "Priced-in" news (e.g., routine board updates, industry-wide news with no specific company impact, news already reflected in market price).
    - **+3 to +7 (Positive):** Bullish catalysts (e.g., analyst upgrades, product launches, revenue beat, new partnerships).
    - **+8 to +10 (Exceptional):** Major breakthroughs (e.g., surprise acquisition, massive earnings beat, game-changing patent approval).

    ### RULES
    1. **Ticker Focus:** Evaluate sentiment ONLY in relation to {company}. Ignore sentiment toward competitors or the broader market unless it directly impacts {company}.
    2. **Novelty Weighting:** Prioritize "New Information." Deduct weight from news that is merely summarizing historical performance.
    3. **Internal Logic:** Even if not outputting text, internally evaluate: (a) Financial impact, (b) Strategic impact, and (c) Market surprise.
    4. **Strict Output:** You must provide the final score. No explanation or commentary.
    5. **Neutral Threshold:** If the news does not directly impact {company}'s financial performance or strategy, assign a score of 0.

    ### INPUT
    Article Title: {title}

    Article Body: {text}

    ### OUTPUT
    Just the integer from -10 to +10. Dont give any explanation or commentary.
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
    response = chat_with_reset_retry(
        OLLAMA_MODEL,
        messages=[
            {
                'role': 'user',
                'content': query,
            },
        ],
        service_name='score',
    )
    logger.debug('ollama response for scoring: %s', response)
    try:
        score = int(response['message']['content'])
    except:
        logger.exception('error parsing score from response')
        return 0
    return score





#Test summary
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_summary(text))

#Test score
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_score('Infosys bags contract',text,'Infosys',True))


    