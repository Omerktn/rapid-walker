from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from threading import Thread
import requests
import threading
import web_crawler
from web_crawler import start_crawler_thread
from web_crawler import get_cit_info
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = "c4ef8faf440bf76712c41e5127a8bf1c"

suggestions_list = []
crawl_started = False

def crawler_sync():
    global suggestions_list
    suggestions_list = get_cit_info()


@app.route('/')
def index():
    return render_template('walker.html')


@app.route('/suggestions')
def suggestions():
    global suggestions_list
    global crawl_started

    text   = request.args.get('jsdata')
    tlimit = request.args.get('tldata')

    if not crawl_started:
        start_crawler_thread(text, float(tlimit))
        crawl_started = True
    else:
        crawler_sync()

    return render_template('suggestions.html', suggestions=suggestions_list)


if __name__ == '__main__':
    app.run(debug=True)
