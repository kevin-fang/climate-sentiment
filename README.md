# Climate Article Sentiment Analysis

Currently scrapes list of CNN news articles (doesn't specifically have to be about climate change). Parses the HTML of each article, breaks up the sentences, then runs through Google's Cloud Natural Language Processing API for sentiment analysis. After retrieving the sentiment, takes the average of all the sentences of the article and returns it. 

Tableau visualization of climate change article data:

![Tableau Visualization](https://raw.githubusercontent.com/kevin-fang/climate-sentiment/master/screenshot.PNG)