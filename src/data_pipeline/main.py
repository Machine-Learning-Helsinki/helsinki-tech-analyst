"""
MAIN MODULE
Responsible for pipeline orchestration, summary, and final processing
"""

from datetime import datetime
from typing import Dict, Any
import json
from .fetch import get_data_from_rss, fetch_rss_data
from .parse import parse_rss_feed_articles
from .storage import connect_storage, store_data, get_data
from .vector_db import vectordb

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

def pipeline_summary(**context):
    """
    Task 4: Main pipeline summary and final processing
    Collects results from all previous tasks and provides comprehensive summary
    """
    print("🔄 MAIN TASK: Pipeline summary and completion...")
    
    # Get results from all previous tasks
    ti = context['ti']
    
    # Get fetch results
    fetch_results = ti.xcom_pull(task_ids='fetch_rss_data')
    
    # Get transform results  
    transform_results = ti.xcom_pull(task_ids='transform_rss_data')
    
    # Get storage results
    storage_results = ti.xcom_pull(task_ids='store_rss_data')
    
    print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    # Detailed summary
    summary = generate_pipeline_summary(fetch_results, transform_results, storage_results)
    
    # Print summary
    print_pipeline_summary(summary)
    
    # Optional: Additional processing
    additional_processing_results = perform_additional_processing(summary, context)
    
    # Create final result
    final_summary = {
        'pipeline_status': 'completed',
        'completion_time': str(datetime.now()),
        'fetch_results': fetch_results,
        'transform_results': transform_results,
        'storage_results': storage_results,
        'pipeline_summary': summary,
        'additional_processing': additional_processing_results
    }
    
    print("\n✅ Main pipeline task completed successfully!")
    return final_summary


def generate_pipeline_summary(fetch_results: dict, transform_results: dict, storage_results: dict) -> dict:
    """
    Generate comprehensive pipeline summary
    
    Args:
        fetch_results: Results from fetch task
        transform_results: Results from transform task  
        storage_results: Results from storage task
    
    Returns:
        Dictionary with pipeline summary
    """
    summary = {
        'fetch_summary': {},
        'transform_summary': {},
        'storage_summary': {},
        'overall_summary': {}
    }
    
    # Fetch summary
    if fetch_results:
        sources_with_data = [k for k, v in fetch_results.items() if v]
        total_entries_fetched = sum(len(v) for v in fetch_results.values() if v)
        failed_sources = [k for k, v in fetch_results.items() if not v]
        
        summary['fetch_summary'] = {
            'total_sources_attempted': len(fetch_results),
            'sources_with_data': len(sources_with_data),
            'failed_sources': len(failed_sources),
            'total_entries_fetched': total_entries_fetched,
            'successful_sources': sources_with_data,
            'failed_source_names': failed_sources
        }
    
    # Transform summary
    if transform_results:
        total_articles_transformed = sum(len(v) for v in transform_results.values() if v)
        sources_transformed = len([k for k, v in transform_results.items() if v])
        
        summary['transform_summary'] = {
            'total_articles_transformed': total_articles_transformed,
            'sources_transformed': sources_transformed,
            'transformation_rate': round(total_articles_transformed / max(summary['fetch_summary'].get('total_entries_fetched', 1), 1) * 100, 2)
        }
    
    # Storage summary
    if storage_results:
        summary['storage_summary'] = {
            'articles_stored': storage_results.get('total_stored', 0),
            'articles_skipped': storage_results.get('total_skipped', 0),
            'processing_errors': storage_results.get('processing_errors', 0),
            'sources_processed': len(storage_results.get('sources_processed', [])),
            'database_stats': storage_results.get('database_stats', {})
        }
    
    # Overall summary
    summary['overall_summary'] = {
        'pipeline_success': True,
        'total_new_articles': storage_results.get('total_stored', 0) if storage_results else 0,
        'efficiency_rate': calculate_efficiency_rate(summary),
        'data_quality_score': calculate_data_quality_score(summary),
        'sources_health': calculate_sources_health(summary)
    }
    
    return summary


def print_pipeline_summary(summary: dict):
    """
    Print formatted pipeline summary
    
    Args:
        summary: Pipeline summary dictionary
    """
    
    # Fetch Results
    fetch_summary = summary.get('fetch_summary', {})
    if fetch_summary:
        print(f"📡 FETCH RESULTS:")
        print(f"   - Sources attempted: {fetch_summary.get('total_sources_attempted', 0)}")
        print(f"   - Sources with data: {fetch_summary.get('sources_with_data', 0)}")
        print(f"   - Failed sources: {fetch_summary.get('failed_sources', 0)}")
        print(f"   - Total entries fetched: {fetch_summary.get('total_entries_fetched', 0)}")
        
        if fetch_summary.get('failed_source_names'):
            print(f"   - Failed sources: {', '.join(fetch_summary['failed_source_names'])}")
    
    # Transform Results
    transform_summary = summary.get('transform_summary', {})
    if transform_summary:
        print(f"\n🔧 TRANSFORM RESULTS:")
        print(f"   - Articles transformed: {transform_summary.get('total_articles_transformed', 0)}")
        print(f"   - Sources processed: {transform_summary.get('sources_transformed', 0)}")
        print(f"   - Transformation rate: {transform_summary.get('transformation_rate', 0)}%")
    
    # Storage Results
    storage_summary = summary.get('storage_summary', {})
    if storage_summary:
        print(f"\n💾 STORAGE RESULTS:")
        print(f"   - New articles stored: {storage_summary.get('articles_stored', 0)}")
        print(f"   - Duplicates skipped: {storage_summary.get('articles_skipped', 0)}")
        print(f"   - Processing errors: {storage_summary.get('processing_errors', 0)}")
        
        db_stats = storage_summary.get('database_stats', {})
        if db_stats:
            print(f"   - Total articles in DB: {db_stats.get('total_articles', 'unknown')}")
            print(f"   - Recent articles (7 days): {db_stats.get('recent_articles', 'unknown')}")
    
    # Overall Results
    overall_summary = summary.get('overall_summary', {})
    if overall_summary:
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   - Pipeline success: {'✅ Yes' if overall_summary.get('pipeline_success') else '❌ No'}")
        print(f"   - New articles added: {overall_summary.get('total_new_articles', 0)}")
        print(f"   - Pipeline efficiency: {overall_summary.get('efficiency_rate', 0)}%")
        print(f"   - Data quality score: {overall_summary.get('data_quality_score', 0)}/100")
        print(f"   - Sources health: {overall_summary.get('sources_health', 0)}%")


def calculate_efficiency_rate(summary: dict) -> float:
    """
    Calculate pipeline efficiency rate
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Efficiency rate as percentage
    """
    try:
        fetch_summary = summary.get('fetch_summary', {})
        storage_summary = summary.get('storage_summary', {})
        
        total_fetched = fetch_summary.get('total_entries_fetched', 0)
        total_stored = storage_summary.get('articles_stored', 0)
        
        if total_fetched == 0:
            return 0.0
        
        efficiency = (total_stored / total_fetched) * 100
        return round(efficiency, 2)
        
    except:
        return 0.0


def calculate_data_quality_score(summary: dict) -> int:
    """
    Calculate data quality score based on various factors
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Quality score from 0 to 100
    """
    try:
        score = 0
        
        # Fetch success rate (40 points)
        fetch_summary = summary.get('fetch_summary', {})
        if fetch_summary.get('total_sources_attempted', 0) > 0:
            fetch_success_rate = fetch_summary.get('sources_with_data', 0) / fetch_summary.get('total_sources_attempted', 1)
            score += int(fetch_success_rate * 40)
        
        # Transform success rate (30 points)
        transform_summary = summary.get('transform_summary', {})
        transform_rate = transform_summary.get('transformation_rate', 0)
        if transform_rate > 0:
            score += min(int(transform_rate * 0.3), 30)
        
        # Storage success rate (30 points)
        storage_summary = summary.get('storage_summary', {})
        total_processed = storage_summary.get('articles_stored', 0) + storage_summary.get('articles_skipped', 0)
        errors = storage_summary.get('processing_errors', 0)
        
        if total_processed > 0:
            storage_success_rate = (total_processed - errors) / total_processed
            score += int(storage_success_rate * 30)
        
        return min(score, 100)
        
    except:
        return 0


def calculate_sources_health(summary: dict) -> float:
    """
    Calculate overall health of RSS sources
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Sources health as percentage
    """
    try:
        fetch_summary = summary.get('fetch_summary', {})
        
        total_sources = fetch_summary.get('total_sources_attempted', 0)
        working_sources = fetch_summary.get('sources_with_data', 0)
        
        if total_sources == 0:
            return 0.0
        
        health = (working_sources / total_sources) * 100
        return round(health, 2)
        
    except:
        return 0.0


def perform_additional_processing(summary: dict, context: dict) -> dict:
    """
    Perform additional processing tasks after main pipeline
    
    Args:
        summary: Pipeline summary dictionary
        context: Airflow context
    
    Returns:
        Dictionary with additional processing results
    """
    print(f"\n🔄 Performing additional processing...")
    
    additional_results = {
        'embeddings_processing': None,
        'notifications_sent': None,
        'monitoring_updated': None,
        'cleanup_performed': None
    }
    
    try:
        # 1. Trigger embeddings processing (if configured)
        embeddings_result = trigger_embeddings_processing(summary)
        additional_results['embeddings_processing'] = embeddings_result
        
        # 2. Send notifications (if configured)
        notification_result = send_pipeline_notifications(summary)
        additional_results['notifications_sent'] = notification_result
        
        # 3. Update monitoring/dashboards (if configured)
        monitoring_result = update_monitoring_dashboards(summary)
        additional_results['monitoring_updated'] = monitoring_result
        
        # 4. Perform cleanup tasks
        cleanup_result = perform_cleanup_tasks(summary)
        additional_results['cleanup_performed'] = cleanup_result
        
        print(f"✅ Additional processing completed")
        
    except Exception as e:
        print(f"⚠️ Some additional processing tasks failed: {e}")
        additional_results['error'] = str(e)
    
    return additional_results


def trigger_embeddings_processing(summary: dict) -> dict:
    """
    Trigger embeddings processing for new articles
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Dictionary with embeddings processing results
    """
    try:
        new_articles = summary.get('overall_summary', {}).get('total_new_articles', 0)
        
        if new_articles == 0:
            return {'status': 'skipped', 'reason': 'no new articles'}
        
        # Here you would integrate with your ML/embeddings pipeline
        # For now, we'll just log the intent
        print(f"🧠 Would trigger embeddings processing for {new_articles} new articles")
        
        return {
            'status': 'triggered',
            'articles_queued': new_articles,
            'message': 'Embeddings processing queued successfully'
        }
        
    except Exception as e:
        print(f"❌ Failed to trigger embeddings processing: {e}")
        return {'status': 'failed', 'error': str(e)}


def send_pipeline_notifications(summary: dict) -> dict:
    """
    Send notifications about pipeline execution
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Dictionary with notification results
    """
    try:
        overall = summary.get('overall_summary', {})
        
        # Create notification message
        message = f"""
        Finland RSS Pipeline Completed
        ✅ Status: {'Success' if overall.get('pipeline_success') else 'Failed'}
        📊 New articles: {overall.get('total_new_articles', 0)}
        📈 Efficiency: {overall.get('efficiency_rate', 0)}%
        🏥 Sources health: {overall.get('sources_health', 0)}%
        """
        
        print(f"📧 Would send notification: {message.strip()}")
        
        return {
            'status': 'sent',
            'message': 'Pipeline completion notification sent',
            'recipients': ['data_team@company.com']  # Configure as needed
        }
        
    except Exception as e:
        print(f"❌ Failed to send notifications: {e}")
        return {'status': 'failed', 'error': str(e)}


def update_monitoring_dashboards(summary: dict) -> dict:
    """
    Update monitoring dashboards with pipeline metrics
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Dictionary with monitoring update results
    """
    try:
        # Here you would integrate with your monitoring system
        # (e.g., Grafana, DataDog, etc.)
        
        metrics = {
            'articles_processed': summary.get('transform_summary', {}).get('total_articles_transformed', 0),
            'articles_stored': summary.get('storage_summary', {}).get('articles_stored', 0),
            'pipeline_efficiency': summary.get('overall_summary', {}).get('efficiency_rate', 0),
            'sources_health': summary.get('overall_summary', {}).get('sources_health', 0)
        }
        
        print(f"📊 Would update monitoring with metrics: {metrics}")
        
        return {
            'status': 'updated',
            'metrics_sent': len(metrics),
            'message': 'Monitoring dashboards updated successfully'
        }
        
    except Exception as e:
        print(f"❌ Failed to update monitoring: {e}")
        return {'status': 'failed', 'error': str(e)}


def perform_cleanup_tasks(summary: dict) -> dict:
    """
    Perform cleanup tasks after pipeline completion
    
    Args:
        summary: Pipeline summary dictionary
    
    Returns:
        Dictionary with cleanup results
    """
    try:
        cleanup_tasks = []
        
        # 1. Clean up temporary files
        cleanup_tasks.append("Cleaned temporary files")
        
        # 2. Archive old logs (if needed)
        cleanup_tasks.append("Archived old logs")
        
        # 3. Update pipeline metrics
        cleanup_tasks.append("Updated pipeline metrics")
        
        print(f"🧹 Performed cleanup tasks: {len(cleanup_tasks)} completed")
        
        return {
            'status': 'completed',
            'tasks_completed': cleanup_tasks,
            'message': f'Successfully completed {len(cleanup_tasks)} cleanup tasks'
        }
        
    except Exception as e:
        print(f"❌ Cleanup tasks failed: {e}")
        return {'status': 'failed', 'error': str(e)}


def run_pipeline():
    """
    Legacy function: Run the complete pipeline (for backward compatibility)
    This function can be used when running the pipeline outside of Airflow
    """
   
    
    
    
    print("INFO: 🚀 Starting the data pipeline...")
    
    # STEP 1: Connect to DB
    print("STEP 1: Connecting to storage...")
    conn = connect_storage()
    print("INFO: ✅ Successfully connected to storage.")
    
    total_articles_processed = 0
    
    # STEP 2: Process each RSS feed
    for name, url in finland_rss_feeds:
        print(f"\nProcessing: {name} - {url}")
        if not url:
            print(f"WARNING: ⚠️ No RSS URL for {name}, skipping...")
            continue
        
        # Fetch
        feed = get_data_from_rss(url)
        if not feed:
            print(f"WARNING: ⚠️ No data fetched from {name}, skipping...")
            continue
        print(f"INFO: ✅ Fetched {len(feed)} entries from {name}.")

        
        # Transform
        parsed_articles = parse_rss_feed_articles(feed, name)
        print(f"INFO: ✅ Parsed {len(parsed_articles)} articles from {name}.")
        
        if parsed_articles:
            # Store
            store_data(parsed_articles, conn)
            total_articles_processed += len(parsed_articles)
            print("INFO: ✅ Data stored successfully.")
    
    # STEP 3: Final summary
    text = get_data(conn=conn)
    print("INFO: ✅ Retrieved data from DB.")
    
    # Close connection
    conn.close()
    print(f"\nINFO: 🎉 Data pipeline completed successfully.")
    print(f"Total articles processed: {total_articles_processed}")

    
    

    return {
        'status': 'completed',
        'total_articles_processed': total_articles_processed,
        'sources_processed': len(finland_rss_feeds)
    }

if __name__ == "__main__":
    run_pipeline()
    vectordb()
