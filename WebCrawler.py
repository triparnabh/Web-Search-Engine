import requests
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
from bs4.element import Comment
import ssl
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import  defaultdict
import string
import operator
import math
from threading import Thread
from tld import get_tld
from tkinter import *
from PIL import Image, ImageTk
from urllib.parse import urlparse
#from PIL import ImageTk, Image

global_result =[]

def main():

    queue.append("https://www.cs.uic.edu")
    threads = []

    for i in range(10):
        process = Thread(target=crawler, args=[visited_list, queue])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()

    #print ("Crawler started...")

    create_web_graph()
    extract_url_content()
    vocab_idf()
    calculate_url_vector_length()

    print("Crawling complete....")
    print("Begin your search...")



def query_dictionary(query_words):

    processed_query_text = text_preprocessing(query_words)
    query_di = {}
    for word in processed_query_text:
        if word not in query_di:
            query_di[word] = 1
        else:
            query_di[word] += 1

    txt.delete(0, 'end')
    calculate_query_idf(query_di)


window = Tk()
window.configure(background="light blue")
window.title("CS582 Information Retrieval Final Project")
window.geometry('300x300')
lbl = Label(window, text="UIC Search Engine", width= 30)
lbl.grid(column=2, row=1)
txt = Entry(window, width=30)
txt.grid(column=4, row=4)
btn3 = Button(window, text="Start Web Crawler", command= main)
btn3.grid(column=5, row=4)
btn1 = Button(window, text="Search for top ten results", command=lambda: query_dictionary(txt.get()))
btn1.grid(column=3, row=5)
btn2 = Button(window, text="Show More Than 10 Results", command=lambda: show_more_results())
btn2.grid(column=3, row=6)
listbox = Listbox(window, width=80, height=35)
listbox.grid(column=4, row=20)

ssl._create_default_https_context = ssl._create_unverified_context

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
punctuations = string.punctuation
reg_pattern = '[' + punctuations + ']'


url_vocab_di = {}
url_vocab_idf = {}
web_graph_di = {}
di2 ={}
data_dictionary = {}
query_idf = {}
tf_idf_ranking = {}
url_di = {}
query_words = []


def crawler(visited_list, queue):

    while (len(visited_list) < 100):
        try:
            list_of_links = []
            current_url = queue.popleft()
            if current_url not in visited_list:
                r = requests.get(current_url)
                if( r.status_code == 200):
                    soup = BeautifulSoup(r.content, "html.parser", from_encoding="iso-8859-1")
                    for link in soup.find_all("a"):
                        url = link.get("href")
                        parsed_url = urlparse(url)

                        if parsed_url.hostname is not None and "uic" in parsed_url.hostname:
                            list_of_links.append(link.get("href").rstrip('/'))


            web_page_text = text_from_html(r.content)
            processed_web_page_text = text_preprocessing(web_page_text)
            if current_url not in data_dictionary:
                data_dictionary[current_url] = {}
                data_dictionary[current_url]['web_page_text'] = processed_web_page_text.copy()
                data_dictionary[current_url]['child_urls'] = list_of_links.copy()
                print(len(visited_list))

            visited_list.append(current_url)

            for complete_url in list_of_links:

                if (complete_url not in visited_list):
                    queue.append(complete_url)
        except Exception:
            pass


def extract_url_content():

    for key in data_dictionary.keys():
        processed_web_page_text = data_dictionary[key]['web_page_text']
        each_url = data_dictionary[key]['child_urls']
        create_inverted_index(processed_web_page_text, key)


def tag_visible(element):

    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):

    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

def text_preprocessing(web_page_text):

    final = []
    for word in web_page_text.split():
        if word not in stop_words:
            y = re.sub(reg_pattern, '', word).lower()
            y = stemmer.stem(y)
            if (y != "") & (y not in stop_words):
                final.append(str(y))
    return final


def create_inverted_index(processed_web_page_text, url):

    for word in processed_web_page_text:
        if word not in url_vocab_di:
            url_vocab_di[word] = {}
        if word in url_vocab_di:
            if url in url_vocab_di[word]:
                url_vocab_di[word][url] += 1
            else:
                url_vocab_di[word][url] = 1

def vocab_idf():

    for word in url_vocab_di:
        url_vocab_idf[word] = (math.log(len(visited_list) / len(url_vocab_di[word]), 2))

    vocab_tf_df()

def vocab_tf_df():
    for word in url_vocab_di:
        for url in url_vocab_di[word]:
            url_vocab_di[word][url] = float(url_vocab_di[word][url] * url_vocab_idf[word])


def calculate_query_idf(query_di):

    for word in query_di:
        if word in url_vocab_di:
            query_idf[word] = (math.log(3500 / len(url_vocab_di[word]), 2))

    find_numerator_of_cosine_similarity(query_di)

def find_numerator_of_cosine_similarity(query_di):

    for q_word in query_di:
        print("{0} -- {1}".format(q_word, url_vocab_idf[q_word]))
        if q_word in url_vocab_di:
            for url in url_vocab_di[q_word]:
                if url in tf_idf_ranking:
                    tf_idf_ranking[url] += (float(url_vocab_di[q_word][url]) * (query_di[q_word] * url_vocab_idf[q_word]))
                else:
                    tf_idf_ranking[url] = (float(url_vocab_di[q_word][url]) * (query_di[q_word] * url_vocab_idf[q_word]))




    calculate_cosine_similarity(query_di)

url_length_vector = {}
def calculate_url_vector_length():
    for word in url_vocab_di:
        for url in url_vocab_di[word]:
            if url in url_length_vector:
                url_length_vector[url] += (url_vocab_di[word][url] * url_vocab_di[word][url])
            else:
                url_length_vector[url] = url_vocab_di[word][url]

    for url in url_length_vector:
        url_length_vector[url] = math.sqrt(url_length_vector[url])


def calculate_cosine_similarity(query_di):
    similarity_list = {}
    similarity_listv2 = {}
    top_twenty_similarity = []

    weight = 0
    for word in query_di:
        if word in url_vocab_di:
            weight += math.pow((query_di[word] * url_vocab_idf[word]), 2)
    query_length = math.sqrt(weight)

    for url in tf_idf_ranking:
        numerator = tf_idf_ranking[url]
        denominator = query_length * url_length_vector[url]
        if denominator!= 0:

            similarity = (numerator/denominator)
            similarity_list[url] = similarity

    for each_url in similarity_list:
        similarity_listv2[each_url] = float((2*(similarity_list[each_url] * di2[url]))/(similarity_list[each_url] + di2[url]))


    k = 1
    for i in (sorted(similarity_listv2.items(), key=operator.itemgetter(1), reverse=True)):
        if k < 40:
            top_twenty_similarity.append(i)
            k = k + 1

    #print(top_twenty_similarity)
    calculate_on_link_score(top_twenty_similarity)


def calculate_on_link_score(top_twenty_similarity):
    global global_result
    listbox.delete(0, END)
    top_ten_urls = []
    url_di = {}
    for link in top_twenty_similarity:
        if link[0] in di2:
            url_di[link[0]] = link[1]

    t = 1
    for x in (sorted(url_di.items(), key=operator.itemgetter(1), reverse=True)):
        if t < 11:
            top_ten_urls.append(x)
            t=t+1
    print(top_ten_urls)

    for i in top_ten_urls:
        listbox.insert(END, i[0])

    global_result = (sorted(url_di.items(), key=operator.itemgetter(1), reverse=True))


def show_more_results():

    more_results = []
    a = 1
    listbox.delete(0, END)

    for x in global_result:
        if a < 26:
            more_results.append(x)
            a = a + 1
    print(more_results)

    for i in more_results:
        listbox.insert(END, i[0])


def create_web_graph():

    for parent_url in data_dictionary:
        if parent_url not in web_graph_di:
            web_graph_di[parent_url] = defaultdict(int)
        for child_url in data_dictionary[parent_url]['child_urls']:
           if child_url in data_dictionary:
                web_graph_di[parent_url][child_url] += 1
                if child_url not in web_graph_di:
                    web_graph_di[child_url] = defaultdict(int)
                web_graph_di[child_url][parent_url] += 1

    #print(web_graph_di)
    calculate_link_score(web_graph_di)


def calculate_link_score(web_graph_di):

    probability = float(1 / len(data_dictionary))
    alpha = 0.85
    constant = ((1 - alpha) * probability)

    for key in data_dictionary:
        if key not in di2:
            di2[key] = probability
    # print(di2)
    for i in range(10):
        for url in web_graph_di:
            sum = 0
            for key in web_graph_di[url]:
                sum += calculate_weight(key, url)
            sum = (alpha * sum) + constant
            di2[url] = sum
    #print(di2)


def calculate_weight(key, url):

    numerator = web_graph_di[key][url]
    denominator = 0

    for w in web_graph_di[key]:
        denominator = denominator + web_graph_di[key][w]
    score = float(((numerator/denominator) * di2[key]))

    return score


visited_list = []
queue = deque([])
window.mainloop()

