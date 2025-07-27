#!/usr/bin/env python3
"""
Test WhatsApp delivery and debug the issue
"""

import requests
import json

def test_whatsapp_webhook():
    """Test the WhatsApp webhook with a simple message"""
    
    url = "https://078031fc4e07.ngrok-free.app/webhook/whatsapp"
    
    # Simulate Twilio webhook data
    data = {
        'Body': 'Hello from test script',
        'From': 'whatsapp:+14699718151',
        'To': 'whatsapp:+14155238886',
        'MessageSid': 'TEST123',
        'AccountSid': 'TEST_ACCOUNT'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'TwilioProxy/1.1'
    }
    
    print("🔍 Testing WhatsApp webhook...")
    print(f"📤 Sending to: {url}")
    print(f"📝 Message: {data['Body']}")
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Webhook responded successfully!")
            
            # Check if it's valid TwiML
            content = response.text
            if "<?xml" in content and "<Response>" in content and "<Message>" in content:
                print("✅ Valid TwiML response generated")
                
                # Extract the message content
                import re
                message_match = re.search(r'<Message>(.*?)</Message>', content, re.DOTALL)
                if message_match:
                    message_content = message_match.group(1)
                    print(f"📱 Message content (first 200 chars): {message_content[:200]}...")
                    print(f"📏 Message length: {len(message_content)} characters")
                else:
                    print("❌ Could not extract message content from TwiML")
            else:
                print("❌ Response is not valid TwiML")
                print(f"📄 Response content: {content[:500]}...")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

def check_twilio_status():
    """Provide guidance on checking Twilio status"""
    print("\n🔧 Troubleshooting Steps:")
    print("1. Check Twilio Console (https://console.twilio.com/)")
    print("2. Go to Messaging > Try it out > Send a WhatsApp message")
    print("3. Verify your WhatsApp sandbox is active")
    print("4. Check if you need to rejoin the sandbox")
    print("5. Verify the webhook URL is correct: https://078031fc4e07.ngrok-free.app/webhook/whatsapp")
    print("6. Check Twilio logs for any delivery errors")

if __name__ == "__main__":
    test_whatsapp_webhook()
    check_twilio_status() 