from typing import List, Dict, Any
import feedparser

def parse_rss_feed_articles(feed: feedparser.FeedParserDict) -> List[Dict[str, Any]]:
    """
    Parses the articles from a feedparser.FeedParserDict object.

    The function is the "T" (transform) in an ETL process. IT cleans and transforms the data into a consistent format.
    Args:
        feed : the Parsed feed object from  get_data_from_rss function.
    Returns:
         A List of dictionaries, each representing an article with keys:
    """
    articles = []
    
    if not feed : 
        return articles
    for entry in feed:
        article = {
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'summary': entry.get('summary', ''),
            'source_name': entry.get("author", "")
        }
        articles.append(article)
        print(f"INFO: Parsed {len(articles)} articles from the feed.")
    
    return articles