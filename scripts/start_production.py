#!/usr/bin/env python3
"""Production start script for Render deployment"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from src.rag.api_server import create_api_server
from src.rag.rag_system import ASURAGSystem

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_production_app():
    """Create production Flask app with RAG system"""
    try:
        logger.info("🚀 Initializing production RAG system...")
        
        # Load configuration
        config = Config()
        
        # Ensure data directories exist
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(config.VECTOR_DB_DIR, exist_ok=True)
        os.makedirs(config.ASU_RAW_DIR, exist_ok=True)
        os.makedirs(config.REDDIT_RAW_DIR, exist_ok=True)
        logger.info("✅ Data directories created/verified")
        
        # Initialize RAG system (lazy loading for production)
        rag_system = ASURAGSystem(config)
        
        # Create Flask app
        app = create_api_server()
        
        # Add health check endpoint
        @app.route('/health')
        def health_check():
            return {'status': 'healthy', 'service': 'asu-rag-api'}, 200
        
        logger.info("✅ Production app created successfully")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create production app: {e}")
        raise

# Create the application instance for gunicorn
app = create_production_app()

# Compatibility alias for gunicorn (in case Render is using cached config)
main = app

if __name__ == '__main__':
    # For direct execution (development)
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"🔧 Development mode - starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 