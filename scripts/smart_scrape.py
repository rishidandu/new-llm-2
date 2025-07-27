#!/usr/bin/env python3
"""
Smart Reddit Scraping Script
Automatically decides between daily fast scraping and periodic historical scraping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.fast_reddit_scraper import FastRedditScraper
from config.settings import Config
import time
import argparse
import datetime
import glob

def check_historical_data_needed(config):
    """Check if historical scraping is needed"""
    historical_dir = os.path.join(config.REDDIT_RAW_DIR, "historical")
    
    if not os.path.exists(historical_dir):
        return True, "No historical directory exists"
    
    # Check for recent historical data (within last 7 days)
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    
    historical_files = glob.glob(f"{historical_dir}/*.jsonl")
    if not historical_files:
        return True, "No historical files found"
    
    # Check if we have recent historical data
    for file_path in historical_files:
        try:
            filename = os.path.basename(file_path)
            file_date = datetime.datetime.strptime(filename.replace('.jsonl', ''), '%Y-%m-%d').date()
            if file_date >= week_ago:
                return False, f"Recent historical data exists: {filename}"
        except:
            continue
    
    return True, "No recent historical data found"

def check_daily_data_needed(config):
    """Check if daily scraping is needed"""
    today = datetime.date.today()
    daily_file = os.path.join(config.REDDIT_RAW_DIR, f"{today}.jsonl")
    
    if not os.path.exists(daily_file):
        return True, "No daily data for today"
    
    # Check file size - if too small, might need re-scraping
    file_size = os.path.getsize(daily_file)
    if file_size < 1000000:  # Less than 1MB
        return True, f"Daily file too small: {file_size} bytes"
    
    return False, f"Daily data exists: {file_size} bytes"

def main():
    parser = argparse.ArgumentParser(description="Smart Reddit Scraping for ASU RAG System")
    parser.add_argument("--force-daily", action="store_true", help="Force daily scraping")
    parser.add_argument("--force-historical", action="store_true", help="Force historical scraping")
    parser.add_argument("--daily-only", action="store_true", help="Only run daily scraping")
    parser.add_argument("--historical-only", action="store_true", help="Only run historical scraping")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    config = Config()
    scraper = FastRedditScraper(config)
    scraper.max_workers = args.workers
    
    print("🧠 Smart Reddit Scraping System")
    print("=" * 50)
    
    # Check what's needed
    daily_needed, daily_reason = check_daily_data_needed(config)
    historical_needed, historical_reason = check_historical_data_needed(config)
    
    print(f"📅 Daily scraping needed: {daily_needed} - {daily_reason}")
    print(f"🏛️ Historical scraping needed: {historical_needed} - {historical_reason}")
    print()
    
    # Determine what to run
    run_daily = args.force_daily or args.daily_only or (daily_needed and not args.historical_only)
    run_historical = args.force_historical or args.historical_only or (historical_needed and not args.daily_only)
    
    if not run_daily and not run_historical:
        print("✅ No scraping needed. All data is up to date!")
        return
    
    total_start_time = time.time()
    
    # Run daily scraping
    if run_daily:
        print("🚀 Starting daily fast scraping...")
        daily_start = time.time()
        
        result = scraper.scrape_all_full_parallel(limit=200)
        
        daily_time = time.time() - daily_start
        if result:
            print(f"✅ Daily scraping completed in {daily_time:.2f} seconds")
            print(f"📁 Saved to: {result}")
        else:
            print("⚠️ Daily scraping failed")
    
    print()
    
    # Run historical scraping
    if run_historical:
        print("🏛️ Starting historical scraping...")
        historical_start = time.time()
        
        historical_dir = os.path.join(config.REDDIT_RAW_DIR, "historical")
        result = scraper.scrape_all_historical(
            limit=1000,  # Higher limit for historical scraping
            time_filters=["week", "month", "year"],
            sort_methods=["hot", "new", "top"],
            output_dir=historical_dir
        )
        
        historical_time = time.time() - historical_start
        if result:
            print(f"✅ Historical scraping completed in {historical_time:.2f} seconds")
            print(f"📁 Saved to: {result}")
        else:
            print("⚠️ Historical scraping failed")
    
    total_time = time.time() - total_start_time
    print()
    print(f"🎉 Smart scraping completed in {total_time:.2f} seconds")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if run_daily:
        print("   • Daily scraping: Run again tomorrow for fresh content")
    if run_historical:
        print("   • Historical scraping: Run again in 7 days for comprehensive data")
    
    if not run_historical:
        next_historical = datetime.date.today() + datetime.timedelta(days=7)
        print(f"   • Next historical scrape recommended: {next_historical}")

if __name__ == "__main__":
    main() 