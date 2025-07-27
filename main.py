#!/usr/bin/env python3
"""
ASU RAG System - Main Entry Point
=================================

Unified interface for scraping, building, and querying the ASU RAG system.
"""

import argparse
import logging
import os
from typing import List

from config.settings import Config
from src.scrapers.asu_web_scraper import ASUScraper
from src.scrapers.reddit_scraper import RedditScraper
from src.rag.rag_system import ASURAGSystem
from src.rag.web_interface import create_app

def setup_logging(config: Config):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def run_scrapers(config: Config, sources: List[str]):
    """Run specified scrapers"""
    print("🔄 Running scrapers...")
    
    if "asu_web" in sources:
        print("📄 Scraping ASU website...")
        asu_scraper = ASUScraper(config)
        asu_scraper.scrape_all()
    
    if "reddit" in sources:
        print("�� Scraping Reddit...")
        reddit_scraper = RedditScraper(config)
        reddit_scraper.scrape_all()
    
    print("✅ Scraping completed!")

def build_rag(config: Config, sources: List[str]):
    """Build RAG system with specified data sources"""
    print("🏗️ Building RAG system...")
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Initialize RAG system
    rag_system = ASURAGSystem(config)
    
    # Ingest data from specified sources
    rag_system.ingest_data(sources)
    
    print("✅ RAG system built successfully!")
    return rag_system

def start_server(config: Config, rag_system: ASURAGSystem = None):
    """Start web interface"""
    print("🌐 Starting web interface...")
    
    if rag_system is None:
        # Initialize RAG system if not provided
        rag_system = ASURAGSystem(config)
    
    # Create and start Flask app
    app = create_app(config, rag_system)
    print(f"�� Server starting at http://localhost:{config.WEB_PORT}")
    app.run(debug=config.DEBUG, host=config.WEB_HOST, port=config.WEB_PORT)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ASU RAG System")
    parser.add_argument("--scrape", action="store_true", help="Run scrapers")
    parser.add_argument("--build-rag", action="store_true", help="Build RAG system")
    parser.add_argument("--serve", action="store_true", help="Start web interface")
    parser.add_argument("--sms", action="store_true", help="Enable SMS functionality")
    parser.add_argument("--sources", nargs="+", default=["asu_web", "reddit"], 
                       choices=["asu_web", "reddit"], help="Data sources to use")
    parser.add_argument("--config", default="config/settings.py", help="Configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config()
    
    # Setup logging
    setup_logging(config)
    
    # Create necessary directories
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(config.VECTOR_DB_DIR, exist_ok=True)
    os.makedirs(config.ASU_RAW_DIR, exist_ok=True)
    os.makedirs(config.REDDIT_RAW_DIR, exist_ok=True)
    
    rag_system = None
    
    # Run scrapers if requested
    if args.scrape:
        run_scrapers(config, args.sources)
    
    # Build RAG system if requested
    if args.build_rag:
        rag_system = build_rag(config, args.sources)
    
    # Start web interface if requested
    if args.serve:
        start_server(config, rag_system)
    
    # If no specific action requested, show help
    if not any([args.scrape, args.build_rag, args.serve]):
        parser.print_help()

if __name__ == "__main__":
    main() 