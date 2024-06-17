# Import necessary libraries
import torch
from transformers import pipeline, AutoTokenizer

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

#Test
# text='Infosys is reportedly set to bag another key government contract. According to a report in Money Control, Infosys has emerged among the top contenders for building the government’s new and upgraded central repository of KYC records—CKYCRR 2.0. Earlier this year, the Central Registry of Securitisation Asset Reconstruction and Security Interest of India (CERSAI), a statutory body under the Reserve Bank of India (RBI) that maintains and operates the system, had floated a tender inviting bids from large IT companies to undertake the critical project.The report claims that the potential bidders, including Infosys, have shared a host of “pre-bidding” suggestions and challenges before finalizing their submissions. The tender is said to be initially planned to be closed on April 16, but was later pushed to May 15 after requests from bidders.'
# print(get_summary(text))

    