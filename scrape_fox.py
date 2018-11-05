from requests.exceptions import RequestException
from contextlib import closing
import re
from lxml import html
import requests
from datetime import datetime
import Algorithmia
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"./climate_sentiment_key.json"

print("Initializing Algorithmia...")
client = Algorithmia.client('sim0ds3RRSQiux4Q9vb47cqyuHe1')
algo = client.algo('nlp/SentimentAnalysis/1.0.5')
def get_algorithmia_sentiment(text):
    algo_in = {
          "document": text
        }
    return algo.pipe(algo_in).result[0]['sentiment']

print("Initializing GCP...")
# Instantiates a GCP client
client = language.LanguageServiceClient()

def get_gcp_sentiment(text):
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score

def get_mean_sentiment(sentiments):
    return sum([x[0] for x in sentiments]) / len(sentiments)

# used to cache the website data - because date information is not located in URL
url_data = {}
def get_url(url):
    if url not in url_data:
        base_url = "https://www.textise.net/showText.aspx?strURL="
        print("Downloading HTML page...")
        page = requests.get(base_url + url.replace(":", "%253A"))
        tree = html.fromstring(page.content)
        print("Finished downloading. Parsing...")

        divs = []
        delete = [" |", r"\n        Other"]
        for div in tree.xpath('//div/text()'):
            divs.append(div.rstrip())

        divs = divs[8:]
        divs = filter(lambda x: x != '', divs)
        divs = filter(lambda x: x not in delete, divs)
        divs = filter(lambda x: "[Image: " not in x, divs)
        date_re = r'(\w+ \d+, \d+)'
        divs = list(divs)
        divs = divs[:-10]
        divs = divs[3:]
        #date = datetime.strptime(divs[0], "Published %B %d, %Y")
        #divs = divs[2:]
        url_data[url] = divs
        return divs
    else:
        #print("Found URL data in cache.")
        return url_data[url]        
    
# get date from Reuters article
def get_date(url):
    divs = get_url(url)
    date = datetime.strptime(divs[0], "Published %B %d, %Y")
    return date

def analyze_sentiment_by_sentences(url, verbose=False):
    # download HTML from simplified page - or pull from cache if already downloaded
    divs = get_url(url)
    date = get_date(url)

    sentiments = []
    for i, sentence in enumerate(divs):
        sentiment = get_gcp_sentiment(sentence)
        sentiments.append((sentiment, sentence))
        if verbose:
            print("Finished analyzing sentence {} of {}".format(i + 1, len(sentences)))
            print("Sentiment: {}".format(sentiment))
            
    return(sentiments, date)#, date)