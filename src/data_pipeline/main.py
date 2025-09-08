from .fetch import get_data_from_rss
from .parse import parse_rss_feed_articles
from .pure_list import process_list_or_dict
from .storage import connect_storage, store_data, get_data
from ..ml_logic.embeddings import process_exceddings
from ..ml_logic.vector_db import vectordatabasePg
import os 
from ..ml_logic.rag import answer_questions



finland_rss_feeds_with_urls = [
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

finland_rss_feeds_with_urls_testing  =  [
   
     ("Hämeen Sanomat RSS Feed", "https://hameensanomat.fi/feed/rss"),
     ("Helsinki Times RSS Feed", "https://helsinkitimes.fi/?format=feed")
]








def run_pipeline():
    """
    Runs the data pipeline to fetch, parse, store, and process RSS feed articles.
    """

    print("INFO: 🚀 Starting the data pipeline...")

    # STEP 1: Connect to DB
    print("STEP 1: Connecting to storage...")
    conn = connect_storage()
    print("INFO: ✅ Successfully connected to storage.")

    # STEP 2: Fetch & Process
    for name, url in finland_rss_feeds_with_urls:
        print(f"\nFetching data from: {name} - {url}")
        if not url:
            print(f"WARNING: ⚠️ No RSS URL for {name}, skipping...")
            continue

        feed = get_data_from_rss(url)
        if not feed:
            print(f"WARNING: ❌ Failed to fetch data from {name}, skipping...")
            continue

        feed = process_list_or_dict(feed)
        if not feed:
            print(f"ERROR: ❌ Could not process feed data for {name}. Skipping...")
            continue

        print("INFO: ✅ Data fetched and processed.")

        # STEP 3: Parse articles
        parsed_articles = parse_rss_feed_articles(feed,name)
        print(f"INFO: ✅ Parsed {len(parsed_articles)} articles from {name}.")

        if parsed_articles:
            print("INFO: Sample articles:")
            for article in parsed_articles[:3]:
                print(f"   • {article['title']} : ({article['link']})")

        # STEP 4: Store in DB
        print("STEP 4: Storing data in DB...")
        store_data(parsed_articles, conn)
        print("INFO: ✅ Data stored successfully.")

        # STEP 5: Retrieve for embeddings
        text = get_data(conn=conn)
        print("INFO: ✅ Retrieved data from DB.")

        # STEP 6: Embeddings
        print("STEP 6: Processing embeddings...")
        
        
        print("INFO: ✅ Embeddings processed successfully.")

    # close db connection
    conn.close()
    print("\nINFO: 🎉 Data pipeline completed successfully.")


if __name__ == "__main__":
    
    run_pipeline()
    vector_db = vectordatabasePg()
    vector_db.upsert_articles()



    
    
