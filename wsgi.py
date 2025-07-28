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
    """Create and return the Flask application with optimizations"""
    try:
        logger.info("🚀 Initializing optimized production app...")
        
        # Import after setting up path
        from config.settings import Config
        from src.rag.optimized_rag_system import OptimizedRAGSystem
        from src.rag.optimized_sms_handler import OptimizedSMSHandler
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        # Ensure data directories exist
        config = Config()
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(config.VECTOR_DB_DIR, exist_ok=True)
        os.makedirs(config.ASU_RAW_DIR, exist_ok=True)
        os.makedirs(config.REDDIT_RAW_DIR, exist_ok=True)
        logger.info("✅ Data directories created/verified")
        
        # Initialize optimized systems
        rag_system = OptimizedRAGSystem(config)
        sms_handler = OptimizedSMSHandler(config, rag_system)
        
        # Create Flask app
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health')
        def health_check():
            return {'status': 'healthy', 'service': 'asu-rag-api-optimized'}, 200
        
        @app.route('/stats')
        def stats():
            """Get system statistics"""
            try:
                return jsonify(rag_system.get_stats())
            except Exception as e:
                logger.error(f"Error in stats endpoint: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/query', methods=['POST'])
        def query():
            """Process a query with optimizations"""
            try:
                body = request.get_json(silent=True) or {}
                question = (body.get('question') or '').strip()
                
                if not question:
                    return jsonify({'error': 'question missing'}), 400
                
                result = rag_system.query(question, top_k=3)  # Reduced for speed
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error in query endpoint: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/', methods=['GET', 'POST'])
        @app.route('/webhook/whatsapp', methods=['POST'])
        def webhook_whatsapp():
            """Handle WhatsApp webhooks with optimizations"""
            if request.method == 'GET':
                return jsonify({
                    'service': 'asu-rag-api-optimized',
                    'status': 'healthy',
                    'endpoints': ['/health', '/stats', '/query', '/webhook/whatsapp']
                })
            
            return sms_handler.handle_incoming_whatsapp()
        
        @app.route('/webhook/sms', methods=['POST'])
        def webhook_sms():
            """Handle SMS webhooks"""
            return sms_handler.handle_incoming_sms()
        
        logger.info("✅ Optimized production app created successfully")
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