# Astronomy Agent 🪐

A Python-based agent that searches for articles on astronomy topics across various sources (arXiv, CrossRef, PubMed) and provides information about astronomical keywords.

## Features

- Search articles on multiple platforms: arXiv, CrossRef, PubMed, and Google Scholar.
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
- `!python3 main.py`
- ## if you are in colab sometimes you must run this code:
- `!python3 /content/astronomy-agent/main.py`


![Screenshot 2025-05-10 012624](https://github.com/user-attachments/assets/ff6d9b53-a433-42ab-ac96-2ec04940f836)


