#!/usr/bin/env python3
"""
Run all scrapers for ASU RAG System
Now with fast Reddit scraping!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.asu_web_scraper import ASUWebScraper
from src.scrapers.fast_reddit_scraper import FastRedditScraper  # Use fast scraper
from config.settings import Config
import time

def main():
    config = Config()
    
    print("🚀 Starting ASU RAG System scrapers...")
    start_time = time.time()
    
    # 1. Fast Reddit scraping
    print("\n📱 Starting fast Reddit scraping...")
    reddit_start = time.time()
    
    reddit_scraper = FastRedditScraper(config)
    reddit_result = reddit_scraper.scrape_all_parallel()
    
    reddit_time = time.time() - reddit_start
    print(f"✅ Reddit scraping completed in {reddit_time:.2f} seconds")
    
    # 2. ASU Web scraping
    print("\n🌐 Starting ASU web scraping...")
    web_start = time.time()
    
    web_scraper = ASUWebScraper(config)
    web_result = web_scraper.scrape_all()
    
    web_time = time.time() - web_start
    print(f"✅ Web scraping completed in {web_time:.2f} seconds")
    
    # Summary
    total_time = time.time() - start_time
    print(f"\n🎉 All scraping completed in {total_time:.2f} seconds!")
    print(f"📊 Reddit: {reddit_time:.2f}s | Web: {web_time:.2f}s")
    
    if reddit_result:
        print(f"📁 Reddit data: {reddit_result}")
    if web_result:
        print(f"📁 Web data: {web_result}")

if __name__ == "__main__":
    main()
