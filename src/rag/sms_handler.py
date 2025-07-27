"""
SMS and WhatsApp Handler for ASU RAG System
===========================================

Handles SMS and WhatsApp interactions via Twilio for the ASU RAG system.
"""

import logging
from typing import Optional
from flask import request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from config.settings import Config
from src.rag.rag_system import ASURAGSystem

logger = logging.getLogger(__name__)

class SMSHandler:
    """Handles SMS and WhatsApp interactions via Twilio"""
    
    def __init__(self, config: Config, rag_system: ASURAGSystem):
        self.config = config
        self.rag_system = rag_system
        self.client = None
        
        # Initialize Twilio client if credentials are available
        if all([config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN]):
            self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            logger.info("Twilio client initialized successfully")
        else:
            logger.warning("Twilio credentials not found. SMS functionality disabled.")
    
    def handle_incoming_sms(self) -> str:
        """Handle incoming SMS and return TwiML response"""
        try:
            # Get the message from the request
            incoming_msg = request.values.get('Body', '').strip()
            from_number = request.values.get('From', '')
            
            logger.info(f"Received SMS from {from_number}: {incoming_msg}")
            
            if not incoming_msg:
                return self._create_response("Please send me a question about ASU!")
            
            # Get response from RAG system
            rag_response = self.rag_system.query(incoming_msg)
            
            # Extract the answer from the response
            if isinstance(rag_response, dict) and 'answer' in rag_response:
                response_text = rag_response['answer']
            else:
                response_text = str(rag_response)
            
            # Truncate response if it's too long for SMS (1600 chars max for Twilio)
            if len(response_text) > 1600:
                response_text = response_text[:1597] + "..."
            
            logger.info(f"Sending response to {from_number}: {str(response_text)[:100] if response_text else 'None'}...")
            
            return self._create_response(response_text)
            
        except Exception as e:
            logger.error(f"Error handling SMS: {e}")
            return self._create_response("Sorry, I encountered an error. Please try again later.")
    
    def handle_incoming_whatsapp(self) -> str:
        """Handle incoming WhatsApp message and return TwiML response"""
        try:
            # Get the message from the request
            incoming_msg = request.values.get('Body', '').strip()
            from_number = request.values.get('From', '')
            
            logger.info(f"Received WhatsApp from {from_number}: {incoming_msg}")
            
            if not incoming_msg:
                return self._create_whatsapp_response("Please send me a question about ASU!")
            
            # Get response from RAG system
            rag_response = self.rag_system.query(incoming_msg)
            
            # Extract the answer from the response
            if isinstance(rag_response, dict) and 'answer' in rag_response:
                response_text = rag_response['answer']
            else:
                response_text = str(rag_response)
            
            # WhatsApp has practical limits for reliable delivery
            if len(response_text) > 1200:
                response_text = response_text[:1197] + "..."
            
            logger.info(f"Sending WhatsApp response to {from_number}: {str(response_text)[:100] if response_text else 'None'}...")
            
            return self._create_whatsapp_response(response_text)
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp: {e}")
            return self._create_whatsapp_response("Sorry, I encountered an error. Please try again later.")
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS via Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.config.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            logger.info(f"SMS sent successfully to {to_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS to {to_number}: {e}")
            return False
    
    def _create_response(self, message: str) -> str:
        """Create TwiML response for SMS"""
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)
    
    def _create_whatsapp_response(self, message: str) -> str:
        """Create TwiML response for WhatsApp"""
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)
    
    def send_whatsapp(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message via Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            # Format WhatsApp number (remove 'whatsapp:' prefix if present)
            if to_number.startswith('whatsapp:'):
                to_number = to_number[9:]
            
            # Add WhatsApp prefix for sending
            whatsapp_number = f"whatsapp:+{to_number}" if not to_number.startswith('+') else f"whatsapp:{to_number}"
            
            message = self.client.messages.create(
                body=message,
                from_=f"whatsapp:{self.config.TWILIO_PHONE_NUMBER}",
                to=whatsapp_number
            )
            logger.info(f"WhatsApp message sent successfully to {to_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending WhatsApp message to {to_number}: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if SMS functionality is available"""
        return self.client is not None and all([
            self.config.TWILIO_ACCOUNT_SID,
            self.config.TWILIO_AUTH_TOKEN,
            self.config.TWILIO_PHONE_NUMBER
        ]) 