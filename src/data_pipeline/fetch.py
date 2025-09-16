import feedparser
import requests

def get_data_from_rss(feed_url: str) -> list:
    """
    Fetches data from an RSS feed URL and returns a list of entries.

    Args:
        feed_url (str): The URL of the RSS feed.

    Returns:
        list: A list of entries from the RSS feed, or None if failed.
    """
    try:
        print()
        print(f"********** Extracting Data From RSS Feed **********\n")
        
        feed = feedparser.parse(feed_url)
        
        # Check for errors
        if hasattr(feed, 'status') and feed.status != 200:
            print(f"Failed to fetch RSS feed, status code: {feed.status}")
            return None
            
        if not hasattr(feed, 'entries') or not feed.entries:
            print("No entries found in the RSS feed.")
            return []
            
        print(f"Successfully fetched {len(feed.entries)} entries from the RSS feed.")
        print(f"********** Data Extraction Completed **********\n")
        
        # Return the entries list, not the entire feed object
        return feed.entries

    except Exception as e:
        print(f"Error fetching data from RSS feed: {e}")
        return None

def get_data_from_api(api_url: str):
    """
    Fetches data from an API endpoint and returns the response.

    Args:
        api_url (str): The API endpoint URL.

    Returns:
        dict: The JSON response from the API, or None if failed.
    """
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data from API, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None