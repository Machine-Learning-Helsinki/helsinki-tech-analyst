from .fetch import get_data_from_rss
from .parse import parse_rss_feed_articles

RSS_FEED_URL ="https://arcticstartup.com/feed/"

def run_pipeline(): 
    """
    Runs the data pipeline to fetch and parse RSS feed articles.
    """

    print("INFO: Starting the data pipeline...")
    
    # Step 1: Fetch data from the RSS feed
    feed = get_data_from_rss(RSS_FEED_URL)
    print(list(feed[0].keys()))
    if feed:
        parsed_articles = parse_rss_feed_articles(feed)
        print(f"INFO: Successfully fetched {len(parsed_articles)} articles from the feed.")
        if parsed_articles:
            for article in parsed_articles[:5]:
                print(f"Article Title: {article['title']}")
                print(f"Link: {article['link']}\n")
        else:
            print("No articles found in the feed.")
    else:
        print("ERROR: Failed to fetch data from the RSS feed.")
    print("INFO: Data pipeline completed.")

if __name__ == "__main__":
    run_pipeline()        
    
    