#!/usr/bin/env python3
"""Flask API server for ASU RAG system - JSON only, no HTML"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from config.settings import Config
from src.rag.rag_system import ASURAGSystem
from src.rag.sms_handler import SMSHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for lazy loading
_rag_system = None
_sms_handler = None
_config = None

def get_rag_system():
    """Lazy load the RAG system to reduce memory usage at startup"""
    global _rag_system, _config
    if _rag_system is None:
        logger.info("🔄 Initializing RAG system (lazy loading)...")
        _config = Config()
        _rag_system = ASURAGSystem(_config)
        logger.info("✅ RAG system initialized")
    return _rag_system

def get_sms_handler():
    """Lazy load the SMS handler"""
    global _sms_handler, _config
    if _sms_handler is None:
        if _config is None:
            _config = Config()
        _sms_handler = SMSHandler(_config, get_rag_system())
    return _sms_handler

def create_api_server() -> Flask:
    """Create a Flask API server that serves only JSON endpoints."""
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend integration
    
    @app.route('/stats')
    def stats():
        """Get system statistics."""
        try:
            rag_system = get_rag_system()
            return jsonify(rag_system.get_stats())
        except Exception as e:
            logger.error(f"Error in stats endpoint: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/query', methods=['POST'])
    def query():
        """Process a query and return results."""
        try:
            body = request.get_json(silent=True) or {}
            question = (body.get('question') or '').strip()
            
            if not question:
                return jsonify({'error': 'question missing'}), 400
            
            rag_system = get_rag_system()
            result = rag_system.query(question, top_k=5)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in query endpoint: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'asu-rag-api'})
    
    @app.route('/', methods=['GET', 'POST'])
    def root():
        """Root endpoint - redirects to WhatsApp webhook for POST requests."""
        if request.method == 'POST':
            # Log the request for debugging
            logger.info(f"🔍 Root POST request received:")
            logger.info(f"   Headers: {dict(request.headers)}")
            logger.info(f"   Form data: {dict(request.form)}")
            logger.info(f"   JSON data: {request.get_json(silent=True)}")
            
            # Check if this looks like a Twilio webhook
            if 'Body' in request.form or 'From' in request.form:
                logger.info(f"   📱 Looks like Twilio webhook, redirecting to WhatsApp handler")
                sms_handler = get_sms_handler()
                return sms_handler.handle_incoming_whatsapp()
            else:
                return jsonify({'error': 'Invalid webhook data'}), 400
        else:
            return jsonify({
                'service': 'asu-rag-api',
                'endpoints': {
                    'health': '/health',
                    'stats': '/stats',
                    'query': '/query',
                    'whatsapp_webhook': '/webhook/whatsapp',
                    'sms_webhook': '/webhook/sms'
                }
            })
    
    @app.route('/webhook/sms', methods=['POST'])
    def sms_webhook():
        """Twilio SMS webhook endpoint."""
        try:
            sms_handler = get_sms_handler()
            return sms_handler.handle_incoming_sms()
        except Exception as e:
            logger.error(f"Error in SMS webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/webhook/whatsapp', methods=['POST'])
    def whatsapp_webhook():
        """Twilio WhatsApp webhook endpoint."""
        try:
            # Log the webhook request for debugging
            logger.info(f"📱 WhatsApp webhook received:")
            logger.info(f"   Headers: {dict(request.headers)}")
            logger.info(f"   Form data: {dict(request.form)}")
            logger.info(f"   Body: {request.form.get('Body', 'No body')}")
            logger.info(f"   From: {request.form.get('From', 'No from')}")
            
            sms_handler = get_sms_handler()
            response = sms_handler.handle_incoming_whatsapp()
            logger.info(f"   Response type: {type(response).__name__}")
            logger.info(f"   Response length: {len(response) if isinstance(response, str) else 'N/A'}")
            return response
        except Exception as e:
            logger.error(f"   ❌ Error in WhatsApp webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/send/whatsapp', methods=['POST'])
    def send_whatsapp():
        """Send WhatsApp message via Twilio."""
        try:
            body = request.get_json(silent=True) or {}
            to_number = body.get('to')
            message = body.get('message')
            
            if not to_number or not message:
                return jsonify({'error': 'to and message required'}), 400
            
            sms_handler = get_sms_handler()
            result = sms_handler.send_whatsapp(to_number, message)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/send/sms', methods=['POST'])
    def send_sms():
        """Send SMS via Twilio."""
        try:
            body = request.get_json(silent=True) or {}
            to_number = body.get('to')
            message = body.get('message')
            
            if not to_number or not message:
                return jsonify({'error': 'to and message required'}), 400
            
            sms_handler = get_sms_handler()
            result = sms_handler.send_sms(to_number, message)
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app

def start_api_server():
    """Start the API server with lazy loading."""
    logger.info("🚀 Starting ASU RAG API server...")
    logger.info("📡 API server starting at http://localhost:3000")
    logger.info("🔗 Endpoints: /stats, /query, /health")
    logger.info("📱 SMS/WhatsApp: /webhook/sms, /webhook/whatsapp, /send/sms, /send/whatsapp")
    
    app = create_api_server()
    app.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == '__main__':
    start_api_server() 