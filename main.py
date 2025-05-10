import requests
import pickle
import os
import time
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET

CACHE_FILE = "/content/astro_cache.pkl"

ASTRO_KEYWORDS = [
    "temperature", "pressure", "velocity", "density", "radiation",
    "gravity", "mass", "magnetic field", "luminosity", "composition",
    "rotation", "orbital period", "distance", "size", "brightness",
    "spectral type", "metallicity", "expansion", "collapse", "fusion"
]


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


def search_arxiv(query, limit=5):
    print(f"\n Searching '{query}' in arXiv...")
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Error accessing arXiv.")
        return []
    soup = BeautifulSoup(response.content, "xml")
    entries = soup.find_all("entry")
    results = []
    for entry in entries:
        results.append({
            "title": entry.title.text.strip(),
            "authors": [author.find("name").text for author in entry.find_all("author")],
            "year": entry.published.text[:4],
            "url": entry.id.text
        })
    return results

def search_pubmed(query, limit=5):
    print(f" Searching '{query}' in PubMed...")
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": limit,
        "retmode": "xml"
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        print(f"❌ HTTP error: {response.status_code}")
        return []

    try:
        root = ET.fromstring(response.text)
        id_list = root.find("IdList")
        if id_list is None or len(id_list) == 0:
            print("❌ No articles found.")
            return []

        ids = [id_elem.text for id_elem in id_list.findall("Id")]

        # Get summaries
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml"
        }
        summary_resp = requests.get(summary_url, params=summary_params)
        summary_root = ET.fromstring(summary_resp.text)

        results = []
        for docsum in summary_root.findall("DocSum"):
            article = {
                "title": "",
                "year": "",
                "authors": [],
                "url": ""
            }

            for item in docsum.findall("Item"):
                name = item.attrib.get("Name")
                if name == "Title":
                    article["title"] = item.text
                elif name == "PubDate":
                    article["year"] = item.text.split(" ")[0]
                elif name == "AuthorList":
                    article["authors"] = [author.text for author in item.findall("Item") if author.text]
                elif name == "DOI":
                    article["url"] = f"https://doi.org/{item.text}" if item.text else ""

            results.append(article)

        return results
    except Exception as e:
        print(f"❌ Error while parsing XML: {e}")
        return []


def search_crossref(query, limit=5):
    print(f"\n Searching '{query}' in CrossRef...")
    url = f"https://api.crossref.org/works?query={query}&rows={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Error accessing CrossRef API.")
        return []
    data = response.json()
    results = []
    for item in data['message']['items']:
        results.append({
            "title": item.get("title", ["No title"])[0],
            "authors": [author.get("given") + " " + author.get("family") for author in item.get("author", [])],
            "year": item.get("published", {}).get("date-parts", [[None]])[0][0],
            "url": item.get("URL", "")
        })
    return results

def display_articles(articles):
    for i, art in enumerate(articles, 1):
        print(f"\n{i}.  {art['title']} ({art['year']})")
        print(f"    Authors: {', '.join(art['authors'])}")
        print(f"    Link: {art['url']}")

def check_keywords(articles):
    print("\n Do you have a specific question related to ypur searched field? (yes/no)")
    if input(">> ").strip().lower() != "yes":
        return
    print(f"\n Choose a keyword to check from the list below:\n{', '.join(ASTRO_KEYWORDS)}")
    keyword = input(" Enter keyword: ").strip().lower()
    matched = []
    for i, art in enumerate(articles, 1):
        if keyword in art["title"].lower():
            matched.append((i, art["title"]))
    if matched:
        print(f"\n✅ Found '{keyword}' mentioned in:")
        for idx, title in matched:
            print(f"   {idx}. {title}")
    else:
        print(f"\n❌ No articles mention '{keyword}' in the title.")

def run_agent():
    cache = load_cache()
    sources = {
        "arxiv": search_arxiv,
        "pubmed": search_pubmed,
        "crossref": search_crossref,  
    }

    while True:
        print("\n Which site would you like to use? (arxiv  / pubmed / crossref) or type 'exit' to quit:")
        site = input(">> ").strip().lower()
        if site == "exit":
            print("Exiting...")
            break
        if site not in sources:
            print("Invalid site. Please choose a valid source.")
            continue

        query = input(" Enter the astronomical object or concept you're interested in: ").strip()
        try:
            limit = int(input("How many articles do you want to retrieve? ").strip())
        except ValueError:
            print(" Please enter a valid number.")
            continue

        key = f"{site}_{query}_{limit}"
        if key in cache:
            print("✅ Retrieved from cache.")
            articles = cache[key]
        else:
            articles = sources[site](query, limit)
            cache[key] = articles
            save_cache(cache)

        if not articles:
            print("❌ No articles found.")
            continue

        display_articles(articles)
        check_keywords(articles)

run_agent()
