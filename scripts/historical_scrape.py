#!/usr/bin/env python3
"""
Historical Reddit Scraping Script
Runs periodically to get comprehensive historical data
Saves to separate historical directory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.fast_reddit_scraper import FastRedditScraper
from config.settings import Config
import time
import argparse
import datetime

def main():
    parser = argparse.ArgumentParser(description="Historical Reddit Scraping for ASU RAG System")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")
    parser.add_argument("--limit", type=int, default=500, help="Posts per subreddit")
    parser.add_argument("--time-filters", nargs="+", default=["week", "month", "year"], 
                       help="Time filters to use")
    parser.add_argument("--sort-methods", nargs="+", default=["hot", "new", "top"], 
                       help="Sorting methods to use")
    parser.add_argument("--force", action="store_true", help="Force run even if recent historical data exists")
    
    args = parser.parse_args()
    
    config = Config()
    scraper = FastRedditScraper(config)
    scraper.max_workers = args.workers
    
    # Create historical directory
    historical_dir = os.path.join(config.REDDIT_RAW_DIR, "historical")
    os.makedirs(historical_dir, exist_ok=True)
    
    # Check if we need to run (avoid daily historical scraping)
    today = datetime.date.today()
    historical_file = os.path.join(historical_dir, f"{today}.jsonl")
    
    if os.path.exists(historical_file) and not args.force:
        print(f"⚠️ Historical data for {today} already exists.")
        print("Use --force to re-run historical scraping.")
        return
    
    print(f"🏛️ Starting historical scrape with {args.workers} workers...")
    print(f"📅 Time filters: {args.time_filters}")
    print(f"📊 Sort methods: {args.sort_methods}")
    print(f"📁 Saving to: {historical_dir}")
    start_time = time.time()
    
    # Historical scrape - get everything like 7-22
    print("📚 Running historical scrape (all time periods)...")
    result = scraper.scrape_all_historical(
        limit=args.limit,
        time_filters=args.time_filters,
        sort_methods=args.sort_methods,
        output_dir=historical_dir  # Save to historical directory
    )
    
    elapsed_time = time.time() - start_time
    
    if result:
        print(f"✅ Historical scrape completed in {elapsed_time:.2f} seconds!")
        print(f"📁 Data saved to: {result}")
        
        # Show data summary
        if os.path.exists(result):
            import subprocess
            try:
                line_count = subprocess.check_output(['wc', '-l', result]).decode().split()[0]
                print(f"📊 Total lines: {line_count}")
            except:
                pass
    else:
        print("⚠️ No historical data found or scrape failed")
    
    print(f"⏱️ Total time: {elapsed_time:.2f} seconds")
    print(f"💡 Next historical scrape recommended: {today + datetime.timedelta(days=7)}")

if __name__ == "__main__":
    main() 