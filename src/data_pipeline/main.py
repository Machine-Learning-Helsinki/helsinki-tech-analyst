from .fetch import get_data_from_rss
from .parse import parse_rss_feed_articles
from .pure_list import process_list_or_dict
from .storage import connect_storage, store_data

RSS_FEED_URL ="https://arcticstartup.com/feed/"

def run_pipeline(): 
    """
    Runs the data pipeline to fetch and parse RSS feed articles.
    """

    print("INFO: Starting the data pipeline...")
    
    # Step 1: Fetch data from the RSS feed
    feed = get_data_from_rss(RSS_FEED_URL) # Extract data from the RSS feed URL
    feed = process_list_or_dict(feed) # Transform the data into a consistent format
    
    
    
    
    print("INFO: Data fetched from RSS feed.")
    
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

    # Step 2: Connect to the storage
    store_data(feed)
    print("INFO: Data pipeline completed.")


if __name__ == "__main__":
    run_pipeline()  

    
    