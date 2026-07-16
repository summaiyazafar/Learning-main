# BBC News Scraper

This small script scrapes headlines, short descriptions (summaries), and links from the BBC News front page and saves results to JSON and CSV.

Prerequisites
- Python 3.8+
- The project already includes many packages; at minimum install:

```bash
pip install requests beautifulsoup4 lxml
```

Quick usage

```bash
python web_scraping/bbc_scraper.py --output web_scraping/output --max 50
```

Outputs
- `web_scraping/output/bbc_news_<timestamp>.json`
- `web_scraping/output/bbc_news_<timestamp>.csv`

Notes
- The script scrapes the front page (`https://www.bbc.com/news`) and extracts promo blocks. If a summary is not available in the block, it will attempt to fetch the article page meta description.
- Respect robots.txt and site Terms of Use. For large-scale collection or frequent polling, prefer official APIs or explicit permission.
