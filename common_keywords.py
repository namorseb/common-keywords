import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import collections
import itertools
import pandas as pd
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')



print("This program returns a graph of the most common 50 words found in your Indeed Job Search")

search = input('Search for: ')
print(search)
city = input('City: ')
state = input('State (eg. WI): ')
keyword = '' #input('Keyword: ')

url_search= search.strip().replace(" ", "%20")
url_city = city.replace(" ", "%20")
url_state = state.strip()
input_url = 'https://www.indeed.com/jobs?q='+url_search+'&l='+url_city+'%2C%20'+url_state+'&vjk=150155c58c26df23&advn=8935830343702940'

# This part of the program was for an earlier version that showed
# the search results in the form of a job title, description, and url

def get_links(URL):
    page = requests.get(URL)
    src = page.content
    soup = BeautifulSoup(src, 'lxml')

    # singles out the results from the rest of the page
    results = soup.find(id = 'resultsCol')
    job_elems = results.find_all('h2', class_='title')
    # iterable container of urls
    urls = []

    for job_elem in job_elems:
        url_elem = job_elem.find('a',href = True)

        urls.append("https://www.indeed.com"+url_elem['href'])

    if urls:
        return urls

def get_nextPage(URL):
    page = requests.get(URL)
    src = page.content
    soup = BeautifulSoup(src, 'lxml')
    pagination_box = soup.find('ul', class_='pagination-list')
    current_page = pagination_box.find('b').text
    next_pageString = str(int(current_page)+1)
    next_page = pagination_box.find(string = next_pageString)
    parent_elem = next_page.parent.parent.parent
    next_urlElem = parent_elem.find('a', href=True)

    next_url = 'https://www.indeed.com'+next_urlElem['href']
    return next_url

# a function that finds a keyword in a page
class wordCounter:
    def __init__ (self, word, countNum):
        self.word = word
        self.countNum = countNum

def find_jobDescriptionList(url, keyword):
    posting_page = requests.get(url)
    source = posting_page.content
    soup_fn = BeautifulSoup(source, 'lxml')
    job_title = soup_fn.find('h3', class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')
    job_company = soup_fn.find('div', class_='icl-u-lg-mr--sm icl-u-xs-mr--xs')
    jobDescriptionText = soup_fn.find(id = 'jobDescriptionText').text
    jobDescription_list = jobDescriptionText.lower().split()
    return jobDescription_list

# Below is the code for the counting keywords function of the program

def countWords(jobDescription_list):
    uniqueWords = []
    stop_words = set(stopwords.words('english'))
    articles = ['a', 'an','of','the','with','is','and','or','as', 'to', 'the', 'for', 'we', 'on', 'you', 'all', 'on', 'in',]
    for word in jobDescription_list:
        if word not in uniqueWords:
            if word not in stop_words:
                uniqueWords.append(word.lower())


    wordObj_list = []
    for item in uniqueWords:
        count = jobDescription_list.count(item)
        wordObj = item

        wordObj_list.append(wordObj)
    return wordObj_list

completeWordList = []
for i in [0,5]:
    url_list = get_links(input_url)
    for url in url_list:
        jobDescript = find_jobDescriptionList(url, keyword)
        completeWordList = completeWordList + countWords(jobDescript)
    i = i+1

counts_completeWord = collections.Counter(completeWordList)

print(counts_completeWord.most_common(30))
clean_words = pd.DataFrame(counts_completeWord.most_common(50), columns =['words','count'])
fig, ax = plt.subplots(figsize=(8,8))
clean_words.sort_values(by='count').plot.barh(x='words', y='count', ax = ax, color ="purple")
ax.set_title("Common Words found in your search (Without Stop Words)")

plt.show()
