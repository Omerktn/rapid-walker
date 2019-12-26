from flask import Flask, render_template, request
from crawler import *
import requests
import threading
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
    global crawl_started
    global suggestions_list

    crawl_started = False
    suggestions_list = []
    initalize_data()

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
