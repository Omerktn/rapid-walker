from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from googlesearch import search
from urllib.parse import urlparse
import re
import time
import threading


class Gsearch_python:
    def __init__(self,name_search):
        self.name = name_search
    def Gsearch(self):
        websites = []
        for siteurl in search(query=self.name,tld='co.in',lang='en',num=10,stop=5,pause=2):
            websites.append(siteurl)
        return websites

def download_website(url):
    uClient = uReq(url, timeout=5)

    page_html = uClient.read()
    uClient.close()

    # HTML Parsing
    page_soup = soup(page_html, "html.parser")
    return page_soup

def crawl_once(url):
    try:
        site = download_website(url)
    except:
        print("-",end="")
        return []

    # Extract links
    branchlinks = []
    for link in site.findAll('a', attrs={'href': re.compile("^http://")}):
        branchlinks.append(link.get('href'))

    return branchlinks

global citation_takers
siteNumerator = {"www.eksisozluk.com":0, "www.google.com":1}
citation_givers = [[1],[]]    ## Kimler kime referans verdi?
citation_takers = [[],[0]]    ## Kimler kimden referans aldı?
crawl_end_info  = []
relationship_s  = []

def calc_link_analysis(siteNum):
    global siteNumerator
    global citation_takers
    global citation_givers

    total_actor_num = len(siteNumerator)

    degree_centrality = len(citation_givers[siteNum]) / float(total_actor_num - 1)
    degree_prestige   = len(citation_takers[siteNum]) / float(total_actor_num - 1)

    return (degree_centrality, degree_prestige)

def get_cit_info():
    global citation_takers
    global siteNumerator
    global crawl_end_info
    global relationship_s
    relationship_s = []
    siteNumeratorList = list(siteNumerator.items())

    for i,taker_list in enumerate(citation_givers):
        for taker_num in taker_list:
            tmp_str = ""
            # Get the name of the website from it's num
            tmp_str += siteNumeratorList[i][0]
            tmp_str += " ---> "
            tmp_str += siteNumeratorList[taker_num][0]

            #print(tmp_str)
            relationship_s.append(tmp_str)

    relationship_s += crawl_end_info

    return relationship_s

def get_site_num(url):
    domain = urlparse(url).netloc

    if domain in siteNumerator:
        site_num = siteNumerator[domain]
    else:
        site_num = int(len(siteNumerator))
        siteNumerator[domain] = site_num
        citation_givers.append([])
        citation_takers.append([])

    return site_num

def start_crawl(seed_term, timelimit):
    keepCrawling = True
    page_num = 1
    i = 0

    gs = Gsearch_python(seed_term)
    current_pages = gs.Gsearch()
    next_pages    = []
    start_time    = time.time()

    while(keepCrawling):
        if len(current_pages) == 0:
            if len(next_pages) == 0:
                break
            else:
                current_pages = next_pages
                next_pages    = []

        current_url = current_pages[-1]
        del current_pages[-1]

        current_site_num = get_site_num(current_url)

        # Crawl
        new_pages = crawl_once(current_url)
        print(len(new_pages))
        page_num += 1

        for longurl in new_pages:
            refer_num = get_site_num(longurl)
            # Referans verenler listesine ekle
            if not refer_num in citation_givers[current_site_num]:
                citation_givers[current_site_num].append(refer_num)

            # Referans alanlar listesine ekle
            if not current_site_num in citation_takers[refer_num]:
                citation_takers[refer_num].append(current_site_num)

        # Delete repeated links
        next_pages += new_pages[:50]
        next_pages  = list(set(next_pages))


        if (time.time() - start_time) >= timelimit:
            global relationship_s
            global siteNumerator
            print("Time has expired.")
            crawl_end_info.append("")
            crawl_end_info.append("!-- Time has expired. ----------------------!")
            crawl_end_info.append("!-> {} pages has crawled.".format(page_num))
            crawl_end_info.append("!-> {} relationship has found.".format(len(relationship_s)))
            crawl_end_info.append("!-- Degree values: -------------------------!")
            crawl_end_info.append("")

            siteNumeratorList = list(siteNumerator.items())

            for (siteName,siteNum) in siteNumeratorList:
                (degree_centrality, degree_prestige) = calc_link_analysis(siteNum)
                crawl_end_info.append(siteName + "'s")
                crawl_end_info.append("Degree Centrality: {0:.3f}\n".format(degree_centrality))
                crawl_end_info.append("Degree Prestige  : {0:.3f}\n".format(degree_prestige))
                crawl_end_info.append("---")

            keepCrawling = False

def start_crawler_thread(input, timelimit):
    crawlerThread = threading.Thread(target = start_crawl, args = (input, timelimit))
    crawlerThread.start()

"""
if __name__ == "__main__":
    crawlerThread = Thread(target = start_crawl, args = ("ggc compiler", 120))
    crawlerThread.start()
"""
