"""
FETCH MODULE
Responsible for downloading RSS feeds from Finnish news sources
"""

import feedparser


def install_packages(**context):
    """Install required packages if they're not available"""
    import subprocess
    import sys
    
    packages = [
        'feedparser',
        'requests', 
        'psycopg2-binary',
        'python-dotenv',
        'deep-translator',
        'beautifulsoup4'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
    
    return "Packages installed successfully"


def fetch_rss_data(**context):
    """
    Task 1: Fetch data from RSS feeds
    Returns: Dictionary with feed data for each source
    """
    # RSS feeds to process
    finland_rss_feeds = [
    ("Finland Today RSS Feed", "https://finlandtoday.fi/feed"),
    ("Helsinki Times RSS Feed", "https://helsinkitimes.fi/?format=feed"),
    ("Iltalehti RSS Feed", "https://www.iltalehti.fi/rss/uutiset.xml"),
    ("Daily Finland RSS Feed", "https://dailyfinland.fi/feed/latest-.."),  # truncated URL as shown
    ("Ilkkapohjalainen RSS Feed", "https://fiare-prod-qt-images.s3.amazonaws.com"),  # truncated or generic placeholder
    ("Länsi-Savo RSS Feed", "https://lansi-savo.fi/feed/rss"),
    ("Hankasalmen Sanomat RSS Feed", "https://hankasalmensanomat.fi/feed/rss"),
    ("Hämeen Sanomat RSS Feed", "https://hameensanomat.fi/feed/rss"),
    ("Kansan Uutiset RSS Feed", "https://ku.fi/feed"),
    ("Aamuposti RSS Feed", "https://aamuposti.fi/feed/rss"),
    ("Etelä-Saimaa RSS Feed", "https://esaimaa.fi/feed/rss"), 
    ("Keskisuomalainen RSS Feed", "https://ksml.fi/feed/rss"),
    ("Salon Seudun Sanomat RSS Feed", "https://sss.fi/feed"),
    ("Borgåbladet RSS Feed", "https://bbl.fi/feeds/feed.xml"),
    ("Etelä-Suomen Sanomat RSS Feed", "https://ess.fi/feed/rss"),
    ("Uusimaa RSS Feed", "https://uusimaa.fi/feed/rss"),
    ("Paikallislehti Sisä-Savo RSS Feed", "https://sisa-savolehti.fi/feed/rss"),
    ("Kouvolan Sanomat RSS Feed", "https://kouvolansanomat.fi/feed/rss"),
    ("Keskilaakso RSS Feed", "https://keskilaakso.fi/feed/rss"),
    ("Kymen Sanomat RSS Feed", "https://kymensanomat.fi/feed/rss"),
    ("Itä-Häme RSS Feed", "https://itahame.fi/feed/rss"),
    ("Savon Sanomat RSS Feed", "https://savonsanomat.fi/feed/rss"),
    ("Sydin RSS Feed", None),  # no explicit RSS URL provided
    ("Kauppalehti RSS Feed", None),  # not shown explicitly
    ("Aamulehti RSS Feed", None),
    ("Hufvudstadsbladet RSS Feed", None),
    ("Nya Åland RSS Feed", "https://nyan.ax/rss"),
    ("Helsingin Sanomat RSS Feed", "https://www.hs.fi/rss/tiede.xml"),
    ("Satakunnan Kansa RSS Feed", "https://satakunnankansa.fi"),
    ("Satakunnan Viikko RSS Feed", "https://sv24.fi"),
    ("JP-Kunnallissanomat RSS Feed", "https://jp-kunnallissanomat.fi"),
    ("Ålandstidningen RSS Feed", "https://alandstidningen.ax"),
    ("Turun Sanomat RSS Feed", "https://ts.fi"),
    ("Västra Nyland RSS Feed", "https://www.vastranyland.fi/rss"),
    ("Österbottens Tidning RSS Feed", "https://osterbottenstidning.fi"),
    ("Järviseutu RSS Feed", "https://jarviseutu-lehti.fi"),
    ("Lapin Kansa RSS Feed", "https://www.lapinkansa.fi/feedit/rss/newest-free/"),
    ("Yle RSS Feed", "https://yle.fi/uutiset/rss/tuoreimmat"),
    ("Tyrvään Sanomat RSS Feed", "https://tyrvaansanomat.fi"),
    ("Satakunnan Kansa » Rauma Region RSS Feed", "https://satakunnankansa.fi/aihe/raum.."),  # truncated
    ("Jämsän Seutu RSS Feed", "https://jamsanseutu.fi"),
    ("Kaleva RSS Feed", "https://kaleva.fi"),
    ("Itä-Savo RSS Feed", "https://www.ita-savo.fi/feed/rss/"),
    ("Vasabladet RSS Feed", "https://vasabladet.fi"),
    ("Ilta-Sanomat RSS Feed", "https://is.fi"),
    ("Nokian Uutiset RSS Feed", "https://www.nokiankylat.fi/sorva/feed/"),
    ("Kainuun Sanomat RSS Feed", "https://www.kainuunsanomat.fi/feed")
]
    
    print("🔄 FETCH TASK: Starting RSS data fetching...")
    
    fetched_data = {}
    successful_fetches = 0
    
    for name, url in finland_rss_feeds:
        print(f"\n📡 Fetching from: {name}")
        print(f"URL: {url}")
        
        if not url:
            print(f"⚠️ No URL provided for {name}, skipping...")
            fetched_data[name] = None
            continue
        
        try:
            print(f"Parsing RSS feed from {url}...")
            feed = feedparser.parse(url)
            
            
            
            # Convert feed entries to serializable format for XCom
            entries = []
            for entry in feed.entries:
                entry_data = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'authors': [author.get('name', '') for author in entry.get('authors', [])] if entry.get('authors') else [],
                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])] if entry.get('tags') else []
                }
                entries.append(entry_data)
            
            fetched_data[name] = entries
            successful_fetches += 1
            print(f"✅ Successfully fetched {len(entries)} entries from {name}")
            
            # Show sample titles
            print("📄 Sample articles:")
            for i, entry in enumerate(entries[:3], 1):
                title = entry.get('title', 'No title')[:50]
                print(f"   {i}. {title}...")
            
        except Exception as e:
            print(f"❌ Error fetching data from {name}: {e}")
            fetched_data[name] = None
    
    print(f"\n📊 FETCH SUMMARY:")
    print(f"   - Sources processed: {len(finland_rss_feeds)}")
    print(f"   - Successful fetches: {successful_fetches}")
    print(f"   - Failed fetches: {len(finland_rss_feeds) - successful_fetches}")
    
    # Count total entries
    total_entries = sum(len(v) for v in fetched_data.values() if v)
    print(f"   - Total entries fetched: {total_entries}")
    
    # Return data for next task via XCom
    return fetched_data


def get_data_from_rss(feed_url: str) -> list:
    """
    Helper function: Fetch data from a single RSS feed URL
    Returns: List of entries or None if failed
    """
    try:
        print(f"********** Extracting Data From RSS Feed **********")
        print(f"Fetching from: {feed_url}")
        
        feed = feedparser.parse(feed_url)
        
        if hasattr(feed, 'status') and feed.status != 200:
            print(f"Failed to fetch RSS feed, status code: {feed.status}")
            return None
            
        if not hasattr(feed, 'entries') or not feed.entries:
            print("No entries found in the RSS feed.")
            return []
            
        print(f"Successfully fetched {len(feed.entries)} entries from the RSS feed.")
        print(f"********** Data Extraction Completed **********")
        
        return feed.entries

    except Exception as e:
        print(f"Error fetching data from RSS feed: {e}")
        return None


def get_data_from_api(api_url: str):
    """
    Helper function: Fetch data from an API endpoint
    Returns: JSON response or None if failed
    """
    import requests
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200 or response.status_code == 301:
            return response.json()
        else:
            print(f"Failed to fetch data from API, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None