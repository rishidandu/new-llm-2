#!/usr/bin/env python3
"""
Test script for WhatsApp functionality
Simulates incoming WhatsApp messages and tests the RAG system response
"""

import requests
import json
import time
from urllib.parse import urlencode

def simulate_whatsapp_webhook(query, from_number="+1234567890"):
    """Simulate a WhatsApp webhook call"""
    print(f"\n📱 Simulating WhatsApp message from {from_number}")
    print(f"Query: {query}")
    print("-" * 50)
    
    # Simulate Twilio webhook data
    webhook_data = {
        'Body': query,
        'From': from_number,
        'To': '+15551234567',  # Your Twilio number
        'MessageSid': 'test_message_sid_123',
        'AccountSid': 'test_account_sid_123'
    }
    
    try:
        response = requests.post(
            'http://localhost:3000/webhook/whatsapp',
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp webhook response:")
            print(response.text)
            
            # Try to parse as TwiML
            if '<?xml' in response.text:
                print("📋 Response is valid TwiML (Twilio format)")
            else:
                print("⚠️ Response is not in TwiML format")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_send_whatsapp(to_number, message):
    """Test sending WhatsApp message"""
    print(f"\n📤 Testing WhatsApp send to {to_number}")
    print(f"Message: {message}")
    print("-" * 50)
    
    try:
        response = requests.post(
            'http://localhost:3000/send/whatsapp',
            json={
                'to_number': to_number,
                'message': message
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Send result: {result}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_whatsapp_queries():
    """Test various WhatsApp queries"""
    print("🚀 Testing WhatsApp Functionality")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "What campus jobs are available at ASU?",
        "How do I get a library job?",
        "Tell me about dining options",
        "What's campus life like?",
        "Help me find a job",
        "MAT 210 course info",
        "Best professors for CS courses"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}/{len(test_queries)}")
        simulate_whatsapp_webhook(query)
        time.sleep(2)  # Brief pause between tests

def test_whatsapp_send():
    """Test sending WhatsApp messages"""
    print("\n📤 Testing WhatsApp Send Functionality")
    print("=" * 60)
    
    # Test sending messages (you'll need to replace with real numbers)
    test_messages = [
        {
            "to_number": "+1234567890",  # Replace with real number
            "message": "Hello! This is a test message from ASU RAG system."
        },
        {
            "to_number": "+1234567890",  # Replace with real number
            "message": "Here's some info about campus jobs: ASU offers various on-campus positions including library aides, dining services, and office assistants."
        }
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n🧪 Send Test {i}/{len(test_messages)}")
        test_send_whatsapp(test["to_number"], test["message"])
        time.sleep(1)

def check_whatsapp_status():
    """Check if WhatsApp functionality is available"""
    print("🔍 Checking WhatsApp Status")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:3000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False
    
    # Test webhook endpoint
    try:
        response = requests.post(
            'http://localhost:3000/webhook/whatsapp',
            data={'Body': 'test', 'From': '+1234567890'},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ WhatsApp webhook endpoint is working")
        else:
            print(f"⚠️ WhatsApp webhook returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ WhatsApp webhook error: {e}")
    
    return True

def main():
    """Main test function"""
    print("📱 ASU RAG System - WhatsApp Testing")
    print("=" * 60)
    
    # Check if server is running
    if not check_whatsapp_status():
        print("\n❌ Please start the API server first:")
        print("   source venv/bin/activate && python scripts/start_api_server.py")
        return
    
    # Test incoming WhatsApp messages
    test_whatsapp_queries()
    
    # Test sending WhatsApp messages
    test_whatsapp_send()
    
    print("\n🎉 WhatsApp testing complete!")
    print("\n📋 Next steps for real WhatsApp integration:")
    print("1. Set up Twilio WhatsApp Sandbox")
    print("2. Configure webhook URLs in Twilio console")
    print("3. Test with real phone numbers")
    print("4. Deploy to production with HTTPS")

if __name__ == "__main__":
    main() 