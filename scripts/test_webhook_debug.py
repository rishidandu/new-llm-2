#!/usr/bin/env python3
"""
WhatsApp Webhook Debug Script
Tests Twilio webhook integration with sanitized data
"""

import requests
import json

def test_webhook_with_real_data():
    """Test webhook with real Twilio data format"""
    
    # Real Twilio webhook data format (with sanitized credentials)
    webhook_data = {
        'SmsMessageSid': 'SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'NumMedia': '0',
        'ProfileName': 'Rishi',
        'MessageType': 'text',
        'SmsSid': 'SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'WaId': '14699718151',
        'SmsStatus': 'received',
        'Body': 'What are some fun parts of campus?',
        'To': 'whatsapp:+14155238886',
        'NumSegments': '1',
        'ReferralNumMedia': '0',
        'MessageSid': 'SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'AccountSid': 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'ChannelMetadata': '{"type":"whatsapp","data":{"context":{"ProfileName":"Rishi","WaId":"14699718151"}}}',
        'From': 'whatsapp:+14699718151',
        'ApiVersion': '2010-04-01'
    }
    
    print("🧪 Testing Webhook with Real Twilio Data")
    print("=" * 50)
    
    # Test root endpoint
    print("\n📤 Testing Root Endpoint (/):")
    try:
        response = requests.post(
            'https://078031fc4e07.ngrok-free.app/',
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response (first 500 chars):")
        print(response.text[:500])
        
        if 'Direct Answer to the Question' in response.text:
            print("✅ RAG system is working!")
        else:
            print("❌ RAG system not responding correctly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test WhatsApp endpoint
    print("\n📤 Testing WhatsApp Endpoint (/webhook/whatsapp):")
    try:
        response = requests.post(
            'https://078031fc4e07.ngrok-free.app/webhook/whatsapp',
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response (first 500 chars):")
        print(response.text[:500])
        
        if 'Direct Answer to the Question' in response.text:
            print("✅ RAG system is working!")
        else:
            print("❌ RAG system not responding correctly")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_twilio_config():
    """Check Twilio configuration"""
    print("\n🔧 Twilio Configuration Check")
    print("=" * 40)
    print("1. Go to Twilio Console: https://console.twilio.com/")
    print("2. Navigate to: Messaging → Try it out → Send a WhatsApp message")
    print("3. Check 'Sandbox settings' tab")
    print("4. Verify webhook URL is set to:")
    print("   https://078031fc4e07.ngrok-free.app/webhook/whatsapp")
    print("   OR")
    print("   https://078031fc4e07.ngrok-free.app/")
    print("5. Method should be: POST")
    print("6. Click 'Save' if you made changes")

def main():
    """Main debug function"""
    print("🔍 WhatsApp Webhook Debug")
    print("=" * 60)
    
    test_webhook_with_real_data()
    check_twilio_config()
    
    print("\n🎯 Next Steps:")
    print("1. Verify Twilio webhook URL is correct")
    print("2. Send a test message to WhatsApp sandbox")
    print("3. Check ngrok dashboard for incoming requests")
    print("4. Check server logs for webhook processing")

if __name__ == "__main__":
    main() 