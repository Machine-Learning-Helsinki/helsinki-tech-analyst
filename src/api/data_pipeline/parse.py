from typing import List, Dict, Any
import feedparser
from deep_translator import GoogleTranslator
import re
from bs4 import BeautifulSoup


  # Good morning


def parse_rss_feed_articles(feed: feedparser.FeedParserDict,name) -> List[Dict[str, Any]]:

    """
    Parses the articles from a feedparser.FeedParserDict object.

    The function is the "T" (transform) in an ETL process. IT cleans and transforms the data into a consistent format.
    Args:
        feed : the Parsed feed object from  get_data_from_rss function.
    Returns:
         A List of dictionaries, each representing an article with keys:
    """
    try:
        articles = []
        
        
    
        if not feed : 
            return articles
        for entry in feed:
            

            article = {
                "link_name" : name,
                'title': translate_to_english(entry.get('title', '')),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': translate_to_english(clean_summary_bs4(entry.get('summary', ''))),
                "authors": [author['name'] for author in entry.get('authors', [])] if entry.get("authors") else [],
                "tags": [translate_to_english(tag['term']) for tag in entry.get('tags', [])] if entry.get("tags") else []
            }
            articles.append(article)
            print(f"INFO: Parsed {len(articles)} articles from the feed.")
        return articles
    except Exception as e:
        print(f"ERROR: Failed to parse articles - {e}")


    
       
    
    
def translate_to_english(text) -> str:
    translator = GoogleTranslator(source="fi", target="en")
    try:
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"ERROR: Translation failed - {e}")
        return text
    


def clean_summary_regex(html_summary: str) -> str:
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', html_summary)
    # Remove extra whitespace/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def clean_summary_bs4(html_summary: str) -> str:
    try:
        soup = BeautifulSoup(html_summary, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"ERROR: BeautifulSoup failed to clean summary - {e}")
        return html_summary