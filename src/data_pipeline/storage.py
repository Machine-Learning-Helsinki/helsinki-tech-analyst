import psycopg2
import os 
from dotenv import load_dotenv

SCHEMA_FILE = './src/data_pipeline/schema.sql'


    

def connect_storage():
    print(f'******** DATABASE CONNECTION ********\n')
    load_dotenv()
    DATABASE_URL = os.getenv("DB_URL")
    
    try:

        conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),  # "db" (service name)
        port=os.getenv("DB_PORT")   # 5432 (inside network)
    )
        print("✅ Database connection established")
        return conn
        
       
            
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: {error}")
    
    

def store_data(feed,conn):
       # your function to connect
    cursor = conn.cursor()
    cursor.execute(open(SCHEMA_FILE, "r").read())
    try:
        if feed:
            for entry in feed:
                cursor.execute(open(SCHEMA_FILE, "r").read())
                cursor.execute(
                    """
                    SELECT 1 FROM articles WHERE link = %s
                    """,
                    (entry.get('link', ''),)   # tuple required
                )
                exists = cursor.fetchone()

                if exists:
                    print(f"INFO: Article with link {entry.get('link', '')} already exists. Skipping insertion.")
                else:
                    cursor.execute(
                        """
                        INSERT INTO articles (link_name, title, link, published, summary, authors,tags)
                        VALUES (%s,%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            entry.get('link_name', ''),
                            entry.get('title', ''),
                            entry.get('link', ''),
                            entry.get('published', ''),
                            entry.get('summary', ''),
                            entry.get('authors', ''),
                            entry.get('tags', '')
                        )
                    )
                  
                    
            conn.commit()
            print("INFO: Data stored successfully.")
        else:
            print("No data to store.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: Failed to store data - {error}")
        conn.rollback()
    
def get_data(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM articles")
        articles = cursor.fetchall()
        print("INFO: Fetch data from the articles table")
        return articles
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: Failed to fetch data - {error}")
        return []


