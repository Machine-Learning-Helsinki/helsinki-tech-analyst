import psycopg2
import os 
from dotenv import load_dotenv


def connect_storage():
    """ Connect to the PostgreSQL database server """
    

def create_tables():
    load_dotenv()
    DATABASE_URL = os.getenv("DB_URL")
    commands = (
        """
        CREATE TABLE articles (
        articles_id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        link TEXT NOT NULL,
        published TIMESTAMP,
        summary TEXT,
        source_name VARCHAR(100)
        );
        """,
    )
    conn = conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    try: 
        
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        print("INFO: Tables created successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: {error}")
