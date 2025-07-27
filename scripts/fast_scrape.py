#!/usr/bin/env python3
"""
Fast Reddit Scraping Script
Optimized for speed and efficiency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.fast_reddit_scraper import FastRedditScraper
from config.settings import Config
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Fast Reddit Scraping for ASU RAG System")
    parser.add_argument("--mode", choices=["full", "incremental", "quick"], default="quick",
                       help="Scraping mode: full (all posts), incremental (recent), quick (fastest)")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--limit", type=int, default=None, help="Posts per subreddit")
    parser.add_argument("--hours", type=int, default=24, help="Hours back for incremental scrape")
    
    args = parser.parse_args()
    
    config = Config()
    scraper = FastRedditScraper(config)
    scraper.max_workers = args.workers
    
    print(f"🚀 Starting {args.mode} scrape with {args.workers} workers...")
    start_time = time.time()
    
    if args.mode == "full":
        # Full scrape - get everything
        print("📊 Running full scrape (all posts)...")
        result = scraper.scrape_all_full_parallel(args.limit or 500)
        
    elif args.mode == "incremental":
        # Incremental scrape - only recent posts
        print(f"🔄 Running incremental scrape (last {args.hours} hours)...")
        result = scraper.scrape_incremental(args.hours)
        
    elif args.mode == "quick":
        # Quick scrape - optimized for speed
        print("⚡ Running quick scrape (optimized for speed)...")
        scraper.optimized_delay = 0.3  # Even faster
        scraper.max_workers = min(args.workers, 15)  # Cap workers
        result = scraper.scrape_all_parallel(args.limit or 100)
    
    elapsed_time = time.time() - start_time
    
    if result:
        print(f"✅ Scrape completed in {elapsed_time:.2f} seconds!")
        print(f"📁 Data saved to: {result}")
    else:
        print("⚠️ No new data found or scrape failed")
    
    print(f"⏱️ Total time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main() 