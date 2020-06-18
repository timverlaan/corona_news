import base64
import feedparser
import io
import requests
import pandas as pd

from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
from flask import Flask
from flask import render_template 
stopwords = set(STOPWORDS)

with open('stops.txt') as f:
    mylist = f.read().splitlines() 

for i in mylist:
    stopwords.add(i)


app = Flask(__name__)

BBC_FEED = pd.read_excel('All_news_corona.xlsx')
LIMIT = 220

class Article:
    def __init__(self, url, image):
        self.url = url
        self.image = image

@app.route("/")
def home():
    # feed = feedparser.parse(BBC_FEED)
    articles = []
    texts = []

    for article in BBC_FEED['Link'][:LIMIT]:
        texts.append(parse_article(article))

    # print(texts)
    cloud = get_wordcloud(" ".join(texts))
    articles.append(Article(url=None, image=cloud))  # no URL for the "meta-article"
    return render_template('home.html', articles=articles)

def parse_article(article_url):
    print("Downloading {}".format(article_url))
    r = requests.get(article_url)
    soup = BeautifulSoup(r.text, "html.parser")
    ps = soup.find_all('p')
    text = "\n".join(p.get_text() for p in ps)
    return text

def get_wordcloud(text):
    pil_img = WordCloud(stopwords=stopwords).generate(text=text).to_image()
    img = io.BytesIO()
    pil_img.save(img, "PNG")
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return img_b64
        
if __name__ == '__main__':
    app.debug = True
    app.run('127.0.0.1')
