import psycopg2
import os 
from dotenv import load_dotenv
from .vector_db import vectordatabasePg





    

def connect_storage():
    print(f'******** DATABASE CONNECTION ********\n')
    load_dotenv()
    DATABASE_URL = os.getenv("DB_URL")
    
    try:

        
        host = os.getenv("DB_HOST", "db")      # default to 'db' if env missing
        port = int(os.getenv("DB_PORT", 5432)) # default to 5432
        user = os.getenv("DB_USER", "ayush")
        password = os.getenv("DB_PASSWORD", "mypassword")
        dbname = os.getenv("DB_NAME", "mydatabase")

        print(f"🔌 Connecting to Postgres at {host}:{port} as {user}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        print("✅ Database connection established")
        return conn
        
       
            
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: {error}")
    
    

def store_data(feed,conn):
       # your function to connect
    cursor = conn.cursor()
    
    vector_database = vectordatabasePg()



    try:
        if feed:
            for entry in feed:
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

            vector_database.upsert_articles()
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


