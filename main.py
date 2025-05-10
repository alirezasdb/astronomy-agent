import requests
from bs4 import BeautifulSoup
import pickle
import os

SEARCH_SOURCES = {
    'arxiv': 'https://arxiv.org/search/?query={}&searchtype=all&source=header',
    'doaj': 'https://doaj.org/search?qs={}',
    'crossref': 'https://api.crossref.org/works?query={}',
    'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/?term={}',
    'google_scholar': 'https://scholar.google.com/scholar?q={}'
}

def search_arxiv(query):
    url = SEARCH_SOURCES['arxiv'].format(query)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    for item in soup.find_all('li', class_='arxiv-result'):
        title = item.find('p', class_='title').text.strip()
        authors = item.find('p', class_='authors').text.strip()
        link = item.find('a')['href']
        articles.append({'title': title, 'authors': authors, 'link': f'https://arxiv.org{link}'})
    return articles

def search_doaj(query):
    url = SEARCH_SOURCES['doaj'].format(query)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    for item in soup.find_all('article'):
        title = item.find('h2').text.strip()
        authors = item.find('span', class_='author').text.strip() if item.find('span', class_='author') else 'Unknown'
        link = item.find('a')['href']
        articles.append({'title': title, 'authors': authors, 'link': link})
    return articles


def search_crossref(query):
    url = SEARCH_SOURCES['crossref'].format(query)
    response = requests.get(url)
    data = response.json()
    articles = []
    for item in data['message']['items']:
        title = item['title'][0]
        authors = ', '.join([author['given'] + ' ' + author['family'] for author in item['author']])
        link = item['URL']
        articles.append({'title': title, 'authors': authors, 'link': link})
    return articles

def search_pubmed(query):
    url = SEARCH_SOURCES['pubmed'].format(query)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    for item in soup.find_all('article'):
        title = item.find('a', class_='title').text.strip()
        authors = item.find('div', class_='authors').text.strip() if item.find('div', class_='authors') else 'Unknown'
        link = item.find('a')['href']
        articles.append({'title': title, 'authors': authors, 'link': f'https://pubmed.ncbi.nlm.nih.gov{link}'})
    return articles


def search_google_scholar(query):
    url = SEARCH_SOURCES['google_scholar'].format(query)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    for item in soup.find_all('div', class_='gs_r gs_or gs_scl'):
        title = item.find('h3').text.strip()
        authors = item.find('div', class_='gs_a').text.strip()
        link = item.find('a')['href']
        articles.append({'title': title, 'authors': authors, 'link': link})
    return articles


def search_articles(query):
    all_articles = []
    

    cache_file = 'data/astro_cache.pkl'
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            cached_data = pickle.load(f)
    else:
        cached_data = {}

    if query in cached_data:
        print("results uploaded from cache")
        return cached_data[query]
    
    
    print("searching on the web...")
    all_articles.extend(search_arxiv(query))
    all_articles.extend(search_doaj(query))
    all_articles.extend(search_crossref(query))
    all_articles.extend(search_pubmed(query))
    all_articles.extend(search_google_scholar(query))


    cached_data[query] = all_articles
    with open(cache_file, 'wb') as f:
        pickle.dump(cached_data, f)
    
    return all_articles


def main():
    query = input(" Please Select a feature(exmp.: gravity, temperature): ")
    articles = search_articles(query)
    
    print("\ Search Results:")
    for idx, article in enumerate(articles):
        print(f"{idx+1}. {article['title']}\n   authers: {article['authors']}\n   link: {article['link']}\n")

if __name__ == '__main__':
    main()
