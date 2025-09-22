"""
STORAGE MODULE
Responsible for database operations and data persistence
"""

import psycopg2
import os 
from dotenv import load_dotenv
from typing import List, Dict, Any
from vector_db import vectordatabasePg



def store_rss_data(**context):
    """
    Task 3: Store the transformed data in PostgreSQL
    Gets data from transform task via XCom
    """
    print("🔄 STORAGE TASK: Starting data storage...")
    
    # Get transformed data from previous task
    ti = context['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_rss_data')
    
    if not transformed_data:
        raise Exception("No transformed data received from transform task")
    
    print(f"📥 Received transformed data from {len(transformed_data)} sources")
    
    # Connect to database
    conn = connect_storage()
    cursor = conn.cursor()
    
    
    try:
        # Create table if it doesn't exist
        create_articles_table(cursor)
        
        total_stored = 0
        total_skipped = 0
        processing_errors = 0
        
        for source_name, articles in transformed_data.items():
            if not articles:
                print(f"⚠️ No articles to store for {source_name}")
                continue
            
            print(f"\n💾 Storing articles from: {source_name}")
            print(f"Processing {len(articles)} articles...")
            
            stored_count = 0
            skipped_count = 0
            error_count = 0
            
            for i, article in enumerate(articles, 1):
                try:
                    # Validate article data
                    if not validate_article_for_storage(article):
                        print(f"⚠️ Invalid article data, skipping...")
                        error_count += 1
                        continue
                    
                    # Check if article already exists
                    if article_exists(cursor, article.get('link', '')):
                        skipped_count += 1
                        if i % 20 == 0:  # Don't spam logs
                            print(f"   Processed {i}/{len(articles)} (skipped existing)")
                    else:
                        # Insert new article
                        insert_article(cursor, article)
                        stored_count += 1
                        if i % 20 == 0:  # Progress indicator
                            print(f"   Processed {i}/{len(articles)} (stored {stored_count})")
                        
                except psycopg2.IntegrityError as e:
                    # Handle duplicate key errors
                    skipped_count += 1
                    conn.rollback()
                    continue
                except Exception as e:
                    print(f"❌ Error storing article {i}: {e}")
                    error_count += 1
                    conn.rollback()
                    continue
            
            total_stored += stored_count
            total_skipped += skipped_count  
            processing_errors += error_count
            
            print(f"📊 {source_name} Results:")
            print(f"   - Stored: {stored_count}")
            print(f"   - Skipped (duplicates): {skipped_count}")
            print(f"   - Errors: {error_count}")
        
       
        # Commit all changes
        conn.commit()

       
        
        print(f"\n📊 STORAGE SUMMARY:")
        print(f"   - Total articles stored: {total_stored}")
        print(f"   - Total articles skipped: {total_skipped}")
        print(f"   - Total processing errors: {processing_errors}")
        print(f"   - Sources processed: {len([k for k, v in transformed_data.items() if v])}")
        
        # Get final database stats
        db_stats = get_database_stats(cursor)
        print(f"   - Total articles in database: {db_stats.get('total_articles', 'unknown')}")

        
        
        # Return storage statistics
        return {
            'total_stored': total_stored,
            'total_skipped': total_skipped,
            'processing_errors': processing_errors,
            'sources_processed': list(transformed_data.keys()),
            'database_stats': db_stats
        }
        
    except Exception as error:
        print(f"❌ Storage task failed: {error}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            print("🔌 Database connection closed")


def connect_storage():
    """
    Connect to PostgreSQL database using environment variables
    
    Returns:
        psycopg2 connection object
    """
    print('******** DATABASE CONNECTION ********')
    load_dotenv()
    
    try:
        host = os.getenv("DB_HOST", "postgres")
        port = int(os.getenv("DB_PORT", 5432))
        user = os.getenv("DB_USER", "airflow")
        password = os.getenv("DB_PASSWORD", "airflow")
        dbname = os.getenv("DB_NAME", "airflow")

        print(f"🔌 Connecting to Postgres at {host}:{port} as {user}")
        print(f"   Database: {dbname}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"✅ Database connection established")
        print(f"   PostgreSQL version: {db_version[0] if db_version else 'unknown'}")
        
        return conn
        
    except Exception as error:
        print(f"❌ Database connection failed: {error}")
        print("Please check your database configuration and credentials")
        raise


def create_articles_table(cursor):
    """
    Create the articles table if it doesn't exist
    
    Args:
        cursor: Database cursor object
    """
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                link_name TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                published TEXT,
                summary TEXT,
                authors TEXT[],
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_link_name ON articles(link_name);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published);
        """)
        
        print("✅ Articles table and indexes ensured")
        
    except Exception as e:
        print(f"❌ Failed to create articles table: {e}")
        raise


def validate_article_for_storage(article: dict) -> bool:
    """
    Validate article data before storage
    
    Args:
        article: Article dictionary to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Required fields
    if not article.get('title') or not article.get('link'):
        return False
    
    # Check for reasonable title length
    if len(article.get('title', '')) > 1000:
        print(f"Warning: Title too long ({len(article['title'])} chars)")
        return False
    
    # Check for reasonable summary length
    if len(article.get('summary', '')) > 10000:
        print(f"Warning: Summary too long ({len(article['summary'])} chars)")
        article['summary'] = article['summary'][:10000] + '...'
    
    return True


def article_exists(cursor, link: str) -> bool:
    """
    Check if article with given link already exists
    
    Args:
        cursor: Database cursor
        link: Article URL to check
    
    Returns:
        True if article exists, False otherwise
    """
    try:
        cursor.execute(
            "SELECT 1 FROM articles WHERE link = %s",
            (link,)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking article existence: {e}")
        return False


def insert_article(cursor, article: dict):
    """
    Insert a single article into the database
    
    Args:
        cursor: Database cursor
        article: Article dictionary to insert
    """
    cursor.execute(
        """
        INSERT INTO articles (link_name, title, link, published, summary, authors, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            article.get('link_name', ''),
            article.get('title', ''),
            article.get('link', ''),
            article.get('published', ''),
            article.get('summary', ''),
            article.get('authors', []),
            article.get('tags', [])
        )
    )


def store_data(articles: List[Dict[str, Any]], conn):
    """
    Legacy function: Store articles in database (for backward compatibility)
    
    Args:
        articles: List of article dictionaries
        conn: Database connection
    """
    cursor = conn.cursor()
    vectordb = vectordatabasePg()
    
    try:
        create_articles_table(cursor)
        
        stored_count = 0
        skipped_count = 0
        
        for article in articles:
            try:
                if not validate_article_for_storage(article):
                    continue
                
                if article_exists(cursor, article.get('link', '')):
                    skipped_count += 1
                    print(f"Article already exists: {article.get('title', 'No title')[:50]}...")
                else:
                    insert_article(cursor, article)
                    stored_count += 1
                    print(f"✅ Stored: {article.get('title', 'No title')[:50]}...")
                    
            except psycopg2.IntegrityError:
                skipped_count += 1
                conn.rollback()
                continue
            except Exception as e:
                print(f"Error storing article: {e}")
                conn.rollback()
                continue
                
        
        conn.commit()
        vectordatabasePg.upsert_articles()
        print(f"Storage complete - Stored: {stored_count}, Skipped: {skipped_count}")
        
    except Exception as error:
        print(f"Failed to store data: {error}")
        conn.rollback()
        raise


def get_data(conn, limit: int = None, source: str = None) -> List[tuple]:
    """
    Retrieve articles from database
    
    Args:
        conn: Database connection
        limit: Maximum number of articles to return
        source: Filter by specific source name
    
    Returns:
        List of article tuples
    """
    cursor = conn.cursor()
    
    try:
        query = "SELECT * FROM articles"
        params = []
        
        if source:
            query += " WHERE link_name = %s"
            params.append(source)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        cursor.execute(query, params)
        articles = cursor.fetchall()
        
        print(f"Retrieved {len(articles)} articles from database")
        return articles
        
    except Exception as error:
        print(f"Failed to fetch data: {error}")
        return []


def get_database_stats(cursor) -> dict:
    """
    Get statistics about the articles database
    
    Args:
        cursor: Database cursor
    
    Returns:
        Dictionary with database statistics
    """
    try:
        stats = {}
        
        # Total articles
        cursor.execute("SELECT COUNT(*) FROM articles")
        stats['total_articles'] = cursor.fetchone()[0]
        
        # Articles by source
        cursor.execute("""
            SELECT link_name, COUNT(*) as count 
            FROM articles 
            GROUP BY link_name 
            ORDER BY count DESC
        """)
        stats['articles_by_source'] = dict(cursor.fetchall())
        
        # Recent articles (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM articles 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        stats['recent_articles'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}