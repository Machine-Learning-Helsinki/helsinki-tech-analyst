import feedparser

def get_data_from_rss(feed_url:str) -> feedparser.FeedParserDict:
    """
    Fetches data from an RSS feed URL and returns a list of entries.

    Args:
        feed_url (str): The URL of the RSS feed.

    Returns:
        list: A list of entries from the RSS feed.
    """
    try:
        feed = feedparser.parse(feed_url)
        if 'entries' in feed:
            return feed['entries']
        if feed.status != 200:
            print("Failed to fetch RSS feed, status code:", feed.status)
            return None
        if not feed.entries:
            print("No entries found in the RSS feed.")
        print(f"Successfully fetched {len(feed.entries)} entries from the RSS feed.")
        return feed




    except Exception as e:
        print(f"Error fetching data from RSS feed: {e}")
        return None