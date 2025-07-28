#!/usr/bin/env python3
"""
Simple WSGI entry point for Render deployment
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and return the Flask application"""
    try:
        logger.info("🚀 Initializing production app...")
        
        # Import after setting up path
        from config.settings import Config
        from src.rag.api_server import create_api_server
        
        # Ensure data directories exist
        config = Config()
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(config.VECTOR_DB_DIR, exist_ok=True)
        os.makedirs(config.ASU_RAW_DIR, exist_ok=True)
        os.makedirs(config.REDDIT_RAW_DIR, exist_ok=True)
        logger.info("✅ Data directories created/verified")
        
        # Create Flask app using the existing API server
        app = create_api_server()
        
        # Add health check endpoint
        @app.route('/health')
        def health_check():
            return {'status': 'healthy', 'service': 'asu-rag-api'}, 200
        
        logger.info("✅ Production app created successfully")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create app: {e}")
        raise

# Create the application instance
application = create_app()

# For gunicorn compatibility
app = application

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 8000))
    application.run(host='0.0.0.0', port=port, debug=False) 