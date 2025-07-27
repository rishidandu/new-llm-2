#!/usr/bin/env python3
"""Start web server with existing data (fast startup)"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from src.rag.rag_system import ASURAGSystem
from src.rag.web_interface import create_app

def start_server_fast(config: Config):
    """Start web interface with existing data (no rebuilding)"""
    print("🌐 Starting web interface with existing data...")
    
    # Initialize RAG system without rebuilding
    rag_system = ASURAGSystem(config)
    
    # Create and start Flask app
    app = create_app(config, rag_system)
    print(f"🚀 Server starting at http://localhost:{config.WEB_PORT}")
    print("📊 Using existing vector database - no rebuilding needed!")
    app.run(debug=config.DEBUG, host=config.WEB_HOST, port=config.WEB_PORT)

if __name__ == "__main__":
    config = Config()
    start_server_fast(config) 