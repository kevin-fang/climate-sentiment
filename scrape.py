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

print("Initializing GCP")
# Instantiates a GCP client
client = language.LanguageServiceClient()

def get_gcp_sentiment(text):
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score

def date_from_url(url):
    date_search = r"(\d+)\/(\d+)\/(\d+)"
    return datetime(*[int(x) for x in re.search(date_search, url).groups()])

def get_mean_sentiment(sentiments):
    return sum([x[0] for x in sentiments]) / len(sentiments)


def analyze_sentiment_by_sentences(url, verbose=False):
    # download HTML from simplified page
    base_url = "https://www.textise.net/showText.aspx?strURL="
    if verbose: print("Downloading HTML page...")
    page = requests.get(base_url + url.replace(":", "%253A"))
    tree = html.fromstring(page.content)
    if verbose: print("Finished downloading. Parsing...")
    
    divs = []
    for div in tree.xpath('//div/text()'):
        divs.append(div.rstrip())
    # delete filler text
    delete = ["Español", 'Set edition preference:', u'\xa0 -', "International  Edition", "International Edition", "Find us on", "Read More", 'U.S.', "Arabic", 'International', 'Here are some options:', "Switzerland", " FOLLOW CNN BUSINESS "]
    divs = filter(lambda x: re.sub(' \d+ of \d+', '', x), divs)
    divs = filter(lambda x: x != [], divs)
    divs = filter(lambda x: x != "<div>", divs)
    divs = filter(lambda x: x != "</div>", divs)
    divs = filter(lambda x: x != "\xa0", divs)
    divs = filter(lambda x: x != ".", divs)
    divs = filter(lambda x: x != " |", divs)
    divs = filter(lambda x: x != "", divs)
    divs = filter(lambda x: "/>" not in x, divs)
    divs = filter(lambda x: "</" not in x, divs)
    divs = filter(lambda x: "http" not in x, divs)
    divs = filter(lambda x: "Image:" not in x, divs)
    divs = filter(lambda x: u"\xa0" not in x, divs)
    divs = filter(lambda x: "Facebook Messenger" not in x, divs)
    divs = filter(lambda x: "Hide Caption" not in x, divs)
    divs = filter(lambda x: "MUST WATCH" not in x, divs)
    divs = filter(lambda x: x not in delete, divs)
    divs = "".join(list(divs)[1:-4])
    sentences = [x.rstrip() for x in divs.split(".")]
    sentiments = []
    for i, sentence in enumerate(sentences):
        #sentiments.append(get_algorithmia_sentiment(sentence))
        sentiments.append((get_gcp_sentiment(sentence), sentence))
        if verbose: print("Finished analyzing sentence {} of {}".format(i + 1, len(sentences)))
        
    return sentiments