import psycopg2
from config import config

def create_tables():
    DB_NAME = "helsinki_articles"
    DB_USER = "postgres"
    DB_HOST = "localhost"   
    DB_PORT = "5432" 
    commands = (
        """
        CREATE TABLE articles 
        articles_id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        link TEXT NOT NULL,
        published TIMESTAMP,
        summary TEXT,
        source_name VARCHAR(100)
        );
        """
    )
    conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            port=DB_PORT,
    )
    try: 
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        print("INFO: Tables created successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: {error}")
