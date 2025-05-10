import requests
import pickle
import os
import time
from bs4 import BeautifulSoup

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
    print(f"\n🔍 Searching '{query}' in arXiv...")
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

def search_doaj(query, limit=5):
    print(f"🔍 Searching for '{query}' in DOAJ...")
    url = f"https://doaj.org/api/v2/search/articles/{query}"
    response = requests.get(url)

    try:
        data = response.json()
        if isinstance(data, list):
            results = []
            for item in data[:limit]:
                if isinstance(item, dict):
                    bibjson = item.get("bibjson", {})
                    results.append({
                        "title": bibjson.get("title", "No title"),
                        "authors": ", ".join([a.get("name", "") for a in bibjson.get("author", [])]),
                        "year": bibjson.get("year", "Unknown"),
                        "url": bibjson.get("link", [{}])[0].get("url", "")
                    })
            return results
        else:
            print("❌ Unexpected DOAJ data format.")
            return []
    except Exception as e:
        print("❌ Failed to parse DOAJ response:", e)
        return []


def search_crossref(query, limit=5):
    print(f"\n Searching '{query}' in CrossRef...")
    url = f"https://api.crossref.org/works?query={query}&rows={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Error accessing CrossRef.")
        return []
    data = response.json().get("message", {}).get("items", [])
    results = []
    for item in data:
        results.append({
            "title": item.get("title", ["No title"])[0],
            "authors": [f"{a.get('given', '')} {a.get('family', '')}" for a in item.get("author", [])] if "author" in item else [],
            "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
            "url": item.get("URL", "")
        })
    return results


def search_pubmed(query, limit=5):
    print(f"\n Searching '{query}' in PubMed...")
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={limit}&retmode=json"
    search_res = requests.get(search_url)
    if search_res.status_code != 200:
        print("❌ Error accessing PubMed.")
        return []
    ids = search_res.json()["esearchresult"]["idlist"]
    if not ids:
        return []
    ids_str = ",".join(ids)
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
    fetch_res = requests.get(fetch_url)
    summaries = fetch_res.json().get("result", {})
    results = []
    for pid in ids:
        summary = summaries.get(pid, {})
        results.append({
            "title": summary.get("title", "No title"),
            "authors": [a["name"] for a in summary.get("authors", [])] if "authors" in summary else [],
            "year": summary.get("pubdate", "").split(" ")[0],
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
        })
    return results

def search_google_scholar(query, limit=5):
    print(f"\n Searching '{query}' in Google Scholar...")
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://scholar.google.com/scholar?q={query}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Error accessing Google Scholar.")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    entries = soup.select(".gs_ri")
    results = []
    for entry in entries[:limit]:
        title_el = entry.select_one(".gs_rt")
        title = title_el.text if title_el else "No title"
        url = title_el.a["href"] if title_el and title_el.a else ""
        author_year = entry.select_one(".gs_a").text if entry.select_one(".gs_a") else ""
        year = author_year[-4:] if author_year[-4:].isdigit() else "N/A"
        authors = author_year.split("-")[0].strip().split(",") if "-" in author_year else []
        results.append({
            "title": title,
            "authors": authors,
            "year": year,
            "url": url
        })
    return results


def display_articles(articles):
    for i, art in enumerate(articles, 1):
        print(f"\n{i}.  {art['title']} ({art['year']})")
        print(f"    Authors: {', '.join(art['authors'])}")
        print(f"    Link: {art['url']}")
        
def check_keywords(articles):
    print("\n Do you have a specific question related to astronomy? (yes/no)")
    if input(">> ").strip().lower() != "yes":
        return
    print(f"\n🪐 Choose a keyword to check from the list below:\n{', '.join(ASTRO_KEYWORDS)}")
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
        "doaj": search_doaj,
        "crossref": search_crossref,
        "pubmed": search_pubmed,
        "scholar": search_google_scholar,
    }

    while True:
        print("\n🌐 Which site would you like to use? (arxiv / doaj / crossref / pubmed / scholar) or type 'exit' to quit:")
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
