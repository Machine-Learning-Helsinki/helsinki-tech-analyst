import psycopg2
import os 
from dotenv import load_dotenv

SCHEMA_FILE = './src/data_pipeline/schema.sql'


    

def connect_storage():
    print(f'******** DATABASE CONNECTION ********\n')
    load_dotenv()
    DATABASE_URL = os.getenv("DB_URL")
    
    conn  = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("✅ Database connection established")
    try: 
        
        with conn.cursor() as cursor:
            # Create table if it does not exist
            print(f"Reading Schema File From: {SCHEMA_FILE}")
            with open(SCHEMA_FILE, 'r') as file:
                schema = file.read()
            
            conn.commit()
            
        return conn
            
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: {error}")
    
    

def store_data(feed):
    conn = connect_storage()   # your function to connect
    cursor = conn.cursor()
    
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
                        INSERT INTO articles (title, link, published, summary, source_name)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            entry.get('title', ''),
                            entry.get('link', ''),
                            entry.get('published', ''),
                            entry.get('summary', ''),
                            entry.get('source_name', '')
                        )
                    )
            conn.commit()
            print("INFO: Data stored successfully.")
        else:
            print("No data to store.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: Failed to store data - {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()