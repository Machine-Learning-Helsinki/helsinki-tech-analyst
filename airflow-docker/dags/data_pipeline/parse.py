"""
TRANSFORM MODULE
Responsible for cleaning, translating, and structuring RSS feed data
"""

from typing import List, Dict, Any
from deep_translator import GoogleTranslator
import re
from bs4 import BeautifulSoup


def transform_rss_data(**context):
    """
    Task 2: Transform/Parse the fetched RSS data
    Gets data from fetch task via XCom and returns transformed data
    """
    print("🔄 TRANSFORM TASK: Starting data transformation...")
    
    # Get data from previous task
    ti = context['ti']
    fetched_data = ti.xcom_pull(task_ids='fetch_rss_data')
    
    if not fetched_data:
        raise Exception("No data received from fetch task")
    
    print(f"📥 Received data from {len(fetched_data)} sources")

    transformed_data = {}
    total_articles = 0
    
    for source_name, entries in fetched_data.items():
        if not entries:
            print(f"⚠️ No entries to transform for {source_name}")
            transformed_data[source_name] = []
            continue
        
        print(f"\n🔧 Transforming data from: {source_name}")
        print(f"Processing {len(entries)} entries...")
        
        articles = []
        for i, entry in enumerate(entries, 1):
            try:
                # Transform each article
                article = {
                    "link_name": source_name,
                    'title': translate_to_english(entry.get('title', '')),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': translate_to_english(clean_summary_bs4(entry.get('summary', ''))),
                    'authors': [translate_to_english(author) for author in entry.get('authors', [])],
                    'tags': [translate_to_english(tag) for tag in entry.get('tags', [])]
                }
                articles.append(article)
                
                if i % 10 == 0:  # Progress indicator
                    print(f"   Processed {i}/{len(entries)} articles...")
                
            except Exception as e:
                print(f"❌ Error transforming article {i}: {e}")
                continue
        
        transformed_data[source_name] = articles
        total_articles += len(articles)
        print(f"✅ Transformed {len(articles)} articles from {source_name}")
        
        # Show sample articles
        print("📖 Sample transformed articles:")
        for i, article in enumerate(articles[:2], 1):
            title = article.get('title', 'No title')[:50]
            summary = article.get('summary', 'No summary')[:30]
            print(f"   {i}. {title}...")
            print(f"      Summary: {summary}...")
    
    print(f"\n📊 TRANSFORM SUMMARY:")
    print(f"   - Total articles transformed: {total_articles}")
    print(f"   - Sources processed: {len([k for k, v in transformed_data.items() if v])}")
    
    # Return transformed data for storage task
    return transformed_data


def parse_rss_feed_articles(feed: list, name: str) -> List[Dict[str, Any]]:
    """
    Helper function: Parse articles from RSS feed entries
    
    Args:
        feed: List of RSS feed entries
        name: Name of the RSS source
    
    Returns:
        List of dictionaries with parsed article data
    """
    try:
        articles = []
        
        if not feed:
            return articles
            
        print(f"Parsing {len(feed)} articles from {name}...")
        
        for entry in feed:
            try:
                article = {
                    "link_name": name,
                    'title': translate_to_english(entry.get('title', '')),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': translate_to_english(clean_summary_bs4(entry.get('summary', ''))),
                    'authors': [translate_to_english(author.get('name', '')) for author in entry.get('authors', [])] if entry.get('authors') else [],
                    'tags': [translate_to_english(tag.get('term', '')) for tag in entry.get('tags', [])] if entry.get('tags') else []
                }
                articles.append(article)
            except Exception as e:
                print(f"Error parsing individual article: {e}")
                continue
                
        print(f"Successfully parsed {len(articles)} articles from {name}")
        return articles
        
    except Exception as e:
        print(f"Failed to parse articles from {name}: {e}")
        return []


def translate_to_english(text: str) -> str:
    """
    Translate Finnish text to English using Google Translator
    
    Args:
        text: Text to translate
    
    Returns:
        Translated text or original text if translation fails
    """
    if not text or len(text.strip()) == 0:
        return text
    
    # Skip translation if text is already in English (basic check)
    if is_likely_english(text):
        return text
        
    try:
        translator = GoogleTranslator(source="fi", target="en")
        translated = translator.translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation failed for text: {text[:50]}... Error: {e}")
        return text


def is_likely_english(text: str) -> bool:
    """
    Simple heuristic to check if text is likely already in English
    
    Args:
        text: Text to check
    
    Returns:
        True if text appears to be English
    """
    # Common English words that rarely appear in Finnish
    english_indicators = ['the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'for', 'with', 'as', 'by']
    
    text_lower = text.lower()
    english_word_count = sum(1 for word in english_indicators if f' {word} ' in f' {text_lower} ')
    
    # If we find several English indicators, assume it's already English
    return english_word_count >= 2


def clean_summary_bs4(html_summary: str) -> str:
    """
    Clean HTML tags from summary text using BeautifulSoup
    
    Args:
        html_summary: HTML string to clean
    
    Returns:
        Plain text without HTML tags
    """
    try:
        if not html_summary:
            return ""
            
        soup = BeautifulSoup(html_summary, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        print(f"HTML cleaning failed: {e}")
        return html_summary


def clean_summary_regex(html_summary: str) -> str:
    """
    Alternative method: Clean HTML tags using regex
    
    Args:
        html_summary: HTML string to clean
    
    Returns:
        Plain text without HTML tags
    """
    if not html_summary:
        return ""
        
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', html_summary)
    # Remove extra whitespace/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def validate_article_data(article: dict) -> bool:
    """
    Validate that article data contains required fields
    
    Args:
        article: Article dictionary to validate
    
    Returns:
        True if article is valid, False otherwise
    """
    required_fields = ['title', 'link']
    
    for field in required_fields:
        if not article.get(field):
            print(f"Warning: Article missing required field '{field}'")
            return False
    
    return True


def enrich_article_data(article: dict) -> dict:
    """
    Add additional computed fields to article data
    
    Args:
        article: Article dictionary to enrich
    
    Returns:
        Enhanced article dictionary
    """
    # Add computed fields
    article['title_length'] = len(article.get('title', ''))
    article['summary_length'] = len(article.get('summary', ''))
    article['has_authors'] = len(article.get('authors', [])) > 0
    article['has_tags'] = len(article.get('tags', [])) > 0
    
    # Extract domain from link
    if article.get('link'):
        try:
            from urllib.parse import urlparse
            domain = urlparse(article['link']).netloc
            article['domain'] = domain
        except:
            article['domain'] = 'unknown'
    
    return article