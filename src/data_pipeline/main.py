from .fetch import get_data_from_rss
from .parse import parse_rss_feed_articles
from .pure_list import process_list_or_dict
from .storage import connect_storage, store_data, get_data
from ..ml_logic.embeddings import process_exceddings
from ..ml_logic.vector_db import vectordatabasePg
import os 
from ..ml_logic.rag import answer_questions


RSS_FEED_URL = "https://arcticstartup.com/feed/"


def run_pipeline(): 
    """
    Runs the data pipeline to fetch, parse, store, and process RSS feed articles.
    """

    print("INFO: 🚀 Starting the data pipeline...")

    # Step 1: Fetch data from the RSS feed
    print("STEP 1: Fetching data from RSS feed...")
    feed = get_data_from_rss(RSS_FEED_URL)
    feed = process_list_or_dict(feed)
    print("INFO: ✅ Data fetched and processed from RSS feed.")

    if feed:
        print("STEP 2: Parsing articles...")
        parsed_articles = parse_rss_feed_articles(feed)
        print(f"INFO: ✅ Parsed {len(parsed_articles)} articles from the feed.")
        
        if parsed_articles:
            print("INFO: Sample articles:")
            for article in parsed_articles[:5]:
                print(f"   • {article['title']} ({article['link']})")
        else:
            print("WARNING: No articles found after parsing.")
    else:
        print("ERROR: ❌ Failed to fetch data from the RSS feed.")
        return  # Stop pipeline if no feed is available

    # Step 3: Connect to storage
    print("STEP 3: Connecting to storage...")
    conn = connect_storage()
    print("INFO: ✅ Successfully connected to storage.")

    # Step 4: Store data in DB
    print("STEP 4: Storing data in the database...")
    store_data(feed, conn)
    print("INFO: ✅ Data stored successfully.")

    # Step 5: Retrieve data and process embeddings
    print("STEP 5: Retrieving data for embeddings...")
    text = get_data(conn=conn)
    print("INFO: ✅ Retrieved data from database.")

    print("STEP 6: Processing embeddings...")
    process_exceddings(text)
    print("INFO: ✅ Embeddings processed successfully.")

    print("INFO: 🎉 Data pipeline completed successfully.")


if __name__ == "__main__":
    
    store = vectordatabasePg()
    store.upsert_articles()
    question = input("Enter your question: ")
    answer_questions(question)
    
