#!/usr/bin/env python3
"""
Test Twilio webhook with ngrok URL
Verifies that the webhook is accessible and working properly
"""

import requests
import json

def test_webhook_endpoint():
    """Test the WhatsApp webhook endpoint"""
    ngrok_url = "https://078031fc4e07.ngrok-free.app"
    webhook_url = f"{ngrok_url}/webhook/whatsapp"
    
    print("🧪 Testing Twilio WhatsApp Webhook")
    print("=" * 50)
    print(f"🌐 ngrok URL: {ngrok_url}")
    print(f"📱 Webhook URL: {webhook_url}")
    print()
    
    # Test data (simulating Twilio webhook)
    test_data = {
        'Body': 'What campus jobs are available at ASU?',
        'From': 'whatsapp:+1234567890',
        'To': 'whatsapp:+15551234567',
        'MessageSid': 'test_message_sid_123',
        'AccountSid': 'test_account_sid_123'
    }
    
    try:
        print("📤 Sending test webhook request...")
        response = requests.post(
            webhook_url,
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook is working!")
            print("📋 Response (first 200 chars):")
            print(response.text[:200] + "...")
            
            # Check if it's valid TwiML
            if '<?xml' in response.text and '<Response>' in response.text:
                print("✅ Valid TwiML response (Twilio format)")
            else:
                print("⚠️ Response is not in TwiML format")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    ngrok_url = "https://078031fc4e07.ngrok-free.app"
    health_url = f"{ngrok_url}/health"
    
    print("\n🏥 Testing Health Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            print(f"📊 Response: {response.json()}")
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

def main():
    """Main test function"""
    print("🚀 Twilio Webhook Testing with ngrok")
    print("=" * 60)
    
    # Test health endpoint first
    test_health_endpoint()
    
    # Test webhook endpoint
    test_webhook_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. Go to Twilio Console: https://console.twilio.com/")
    print("2. Navigate to Messaging → Try it out → Send a WhatsApp message")
    print("3. Set webhook URL to: https://078031fc4e07.ngrok-free.app/webhook/whatsapp")
    print("4. Join your WhatsApp sandbox and send a test message")
    print("5. Monitor requests at: http://localhost:4040")
    print("\n🎉 Ready for real Twilio testing!")

if __name__ == "__main__":
    main() 