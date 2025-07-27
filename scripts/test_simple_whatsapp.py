#!/usr/bin/env python3
"""
Test simple WhatsApp response
"""

import requests

def test_simple_response():
    """Test with a very simple response"""
    
    # Simple test data
    webhook_data = {
        'Body': 'hello',
        'From': 'whatsapp:+14699718151',
        'To': 'whatsapp:+14155238886',
        'MessageSid': 'test_simple_123'
    }
    
    print("🧪 Testing Simple WhatsApp Response")
    print("=" * 40)
    
    try:
        response = requests.post(
            'https://078031fc4e07.ngrok-free.app/webhook/whatsapp',
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print("Response:")
        print(response.text)
        
        # Check if it's valid TwiML
        if '<?xml' in response.text and '<Response>' in response.text:
            print("✅ Valid TwiML response")
        else:
            print("❌ Not valid TwiML")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_twilio_status():
    """Check Twilio status"""
    print("\n🔧 Twilio Status Check")
    print("=" * 30)
    print("1. Go to: https://console.twilio.com/")
    print("2. Navigate to: Messaging → Logs")
    print("3. Look for your recent messages")
    print("4. Check delivery status")
    print("5. Look for any error messages")

def main():
    """Main test function"""
    print("📱 Simple WhatsApp Test")
    print("=" * 50)
    
    test_simple_response()
    check_twilio_status()
    
    print("\n🎯 If webhook works but WhatsApp doesn't receive:")
    print("1. Check Twilio Console → Messaging → Logs")
    print("2. Verify sandbox setup")
    print("3. Try rejoining the sandbox")
    print("4. Check if your number is properly registered")

if __name__ == "__main__":
    main() 