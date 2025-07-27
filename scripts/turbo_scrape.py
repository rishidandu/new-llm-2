#!/usr/bin/env python3
"""
Turbo Reddit Scraping Script
Maximum performance for powerful computers
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
    parser = argparse.ArgumentParser(description="Turbo Reddit Scraping for ASU RAG System")
    parser.add_argument("--mode", choices=["daily", "historical", "both"], default="both", 
                       help="Scraping mode")
    parser.add_argument("--workers", type=int, default=50, help="Number of parallel workers")
    parser.add_argument("--limit", type=int, default=1000, help="Posts per subreddit")
    parser.add_argument("--force", action="store_true", help="Force re-scraping")
    
    args = parser.parse_args()
    
    config = Config()
    scraper = FastRedditScraper(config)
    scraper.max_workers = args.workers
    
    print("🚀 TURBO Reddit Scraping System")
    print("=" * 50)
    print(f"💻 Workers: {args.workers}")
    print(f"📊 Limit: {args.limit} posts per subreddit")
    print(f"⚡ Delay: {config.REDDIT_DELAY}s")
    print()
    
    total_start_time = time.time()
    
    # Run daily scraping
    if args.mode in ["daily", "both"]:
        print("🚀 Starting TURBO daily scraping...")
        daily_start = time.time()
        
        result = scraper.scrape_all_full_parallel(limit=args.limit)
        
        daily_time = time.time() - daily_start
        if result:
            print(f"✅ TURBO daily scraping completed in {daily_time:.2f} seconds")
            print(f"📁 Saved to: {result}")
        else:
            print("⚠️ Daily scraping failed")
    
    print()
    
    # Run historical scraping
    if args.mode in ["historical", "both"]:
        print("🏛️ Starting TURBO historical scraping...")
        historical_start = time.time()
        
        historical_dir = os.path.join(config.REDDIT_RAW_DIR, "historical")
        result = scraper.scrape_all_historical(
            limit=args.limit,
            time_filters=["week", "month", "year"],
            sort_methods=["hot", "new", "top"],
            output_dir=historical_dir
        )
        
        historical_time = time.time() - historical_start
        if result:
            print(f"✅ TURBO historical scraping completed in {historical_time:.2f} seconds")
            print(f"📁 Saved to: {result}")
        else:
            print("⚠️ Historical scraping failed")
    
    total_time = time.time() - total_start_time
    print()
    print(f"🎉 TURBO scraping completed in {total_time:.2f} seconds")
    
    # Performance metrics
    if args.mode == "both":
        print(f"📊 Average time per subreddit: {total_time/len(config.REDDIT_SUBREDDITS):.2f}s")
        print(f"⚡ Posts per second: ~{(args.limit * len(config.REDDIT_SUBREDDITS)) / total_time:.1f}")

if __name__ == "__main__":
    main() 