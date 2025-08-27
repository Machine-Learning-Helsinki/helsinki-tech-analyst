from typing import List, Dict, Any
import feedparser

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
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                "authors": [author['name'] for author in entry.get('authors', [])] if entry.get("authors") else [],
                "tags": [tag['term'] for tag in entry.get('tags', [])] if entry.get("tags") else []
            }
            articles.append(article)
            print(f"INFO: Parsed {len(articles)} articles from the feed.")
    except Exception as e:
        print(f"ERROR: Failed to parse articles - {e}")


    
       
    
    return articles