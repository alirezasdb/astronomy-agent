# Astronomy Agent 🪐

A Python-based agent that searches for articles on astronomy topics across various sources (arXiv, DOAJ, CrossRef, PubMed, Google Scholar) and provides information about astronomical keywords.

## Features

- Search articles on multiple platforms: arXiv, DOAJ, CrossRef, PubMed, and Google Scholar.
- Cache results to avoid redundant searches.
- Check for specific astronomy keywords in article titles.
  
## astro-agent /
-`│
├── data/
│   └── astro_cache.pkl
├── main.py
├── requirements.txt
├── README.md
└── .gitignore`

## Requirements

- `requests`
- `beautifulsoup4`

## Setup

1. Clone the repository:
- `!git clone https://github.com/alirezasdb/astronomy-agent.git`

2. Install dependencies:
- `!pip install -r requirements.txt`
- ## if you are in colab sometimes you must run this code:
- `!pip install -r /content/astronomy-agent/requirements.txt`

3-Running in Google Colab
- ## if you are in colab sometimes you must run this code:
- `!python3 /content/astronomy-agent/main.py`


