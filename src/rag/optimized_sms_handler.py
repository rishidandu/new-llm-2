#!/usr/bin/env python3
"""
Optimized SMS Handler with timeouts and fallback responses
"""

import logging
import time
import signal
from typing import Optional
from flask import request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from config.settings import Config
from src.rag.optimized_rag_system import OptimizedRAGSystem

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Query timeout")

class OptimizedSMSHandler:
    """Optimized SMS handler with timeouts and fallback responses"""
    
    def __init__(self, config: Config, rag_system: OptimizedRAGSystem):
        self.config = config
        self.rag_system = rag_system
        self.client = None
        self.max_query_time = 15  # 15 second timeout
        
        # Initialize Twilio client if credentials are available
        if all([config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN]):
            self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            logger.info("✅ Twilio client initialized successfully")
        else:
            logger.warning("⚠️ Twilio credentials not found. SMS functionality disabled.")
    
    def _get_quick_response(self, question: str) -> Optional[str]:
        """Get quick responses for common questions"""
        question_lower = question.lower().strip()
        
        quick_responses = {
            'hello': "Hi! I'm the ASU assistant. Ask me anything about Arizona State University!",
            'hi': "Hello! I can help you with questions about ASU. What would you like to know?",
            'help': "I can answer questions about ASU academics, campus life, admissions, and more. Just ask!",
            'what is asu': "Arizona State University (ASU) is a public research university in Arizona, known for innovation and academic excellence.",
            'thanks': "You're welcome! Feel free to ask more questions about ASU anytime.",
            'thank you': "You're welcome! Happy to help with ASU information."
        }
        
        for key, response in quick_responses.items():
            if key in question_lower:
                return response
        
        return None
    
    def _execute_with_timeout(self, func, *args, **kwargs):
        """Execute function with timeout"""
        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.max_query_time)
        
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Cancel timeout
            return result
        except TimeoutException:
            logger.warning(f"⏰ Query timeout after {self.max_query_time}s")
            return None
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    def handle_incoming_whatsapp(self):
        """Handle incoming WhatsApp messages with optimizations"""
        try:
            # Get message details
            message_body = request.form.get('Body', '').strip()
            from_number = request.form.get('From', '')
            
            if not message_body:
                logger.warning("Empty message received")
                return self._send_response("Please send a message with your question about ASU.")
            
            logger.info(f"📱 WhatsApp message from {from_number}: {message_body}")
            
            # Check for quick response first
            quick_response = self._get_quick_response(message_body)
            if quick_response:
                logger.info("🚀 Using quick response")
                return self._send_response(quick_response)
            
            # For complex queries, use RAG system with timeout
            start_time = time.time()
            
            # Execute RAG query with timeout
            result = self._execute_with_timeout(
                self.rag_system.query, 
                message_body, 
                top_k=3  # Reduced for speed
            )
            
            query_time = time.time() - start_time
            
            if result is None:
                # Timeout occurred
                response_text = (
                    "I'm processing a lot of requests right now. "
                    "Please try asking a more specific question or try again in a moment."
                )
            else:
                response_text = result.get('answer', 'Sorry, I could not find relevant information.')
                logger.info(f"⚡ Query completed in {query_time:.2f}s")
            
            return self._send_response(response_text)
            
        except Exception as e:
            logger.error(f"❌ Error handling WhatsApp message: {e}")
            fallback_response = (
                "I'm experiencing technical difficulties. "
                "Please try again in a few minutes or contact ASU directly for immediate assistance."
            )
            return self._send_response(fallback_response)
    
    def handle_incoming_sms(self):
        """Handle incoming SMS messages (similar to WhatsApp)"""
        return self.handle_incoming_whatsapp()  # Same logic for now
    
    def _send_response(self, message: str) -> str:
        """Send response via Twilio"""
        try:
            resp = MessagingResponse()
            
            # Limit response length for WhatsApp
            if len(message) > 1600:
                message = message[:1600] + "... (truncated for length)"
            
            resp.message(message)
            
            logger.info(f"📤 Sending response: {message[:100]}...")
            return str(resp)
            
        except Exception as e:
            logger.error(f"❌ Error sending response: {e}")
            # Return empty response to avoid errors
            return str(MessagingResponse())
    
    def send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """Send outgoing WhatsApp message"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=f'whatsapp:{self.config.TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{to_number}'
            )
            logger.info(f"✅ WhatsApp message sent: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
            return False 