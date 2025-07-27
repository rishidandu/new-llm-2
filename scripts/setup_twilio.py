#!/usr/bin/env python3
"""
Twilio Setup Script for ASU RAG System
======================================

This script helps you set up Twilio for SMS functionality.
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Twilio Setup for ASU RAG System")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        create_env_file()
    else:
        print("✅ .env file found")
    
    print("\n📋 To enable SMS and WhatsApp functionality, you need to:")
    print("1. Sign up for a Twilio account at https://www.twilio.com")
    print("2. Get your Account SID and Auth Token from the Twilio Console")
    print("3. Get a Twilio phone number")
    print("4. Add these to your .env file:")
    print("\n   TWILIO_ACCOUNT_SID=your_account_sid_here")
    print("   TWILIO_AUTH_TOKEN=your_auth_token_here")
    print("   TWILIO_PHONE_NUMBER=your_twilio_phone_number_here")
    
    print("\n🔗 Webhook URLs for Twilio:")
    print("   SMS: https://your-domain.com/sms")
    print("   WhatsApp: https://your-domain.com/whatsapp")
    print("   (Replace 'your-domain.com' with your actual domain)")
    
    print("\n📱 To test SMS functionality:")
    print("1. Start the server: python3 main.py --serve --sms")
    print("2. Use ngrok to expose localhost: ngrok http 3000")
    print("3. Set the webhook URL in Twilio to: https://your-ngrok-url.ngrok.io/sms")
    print("4. Text your Twilio number with questions about ASU!")
    
    print("\n💬 To test WhatsApp functionality:")
    print("1. Start the server: python3 main.py --serve --sms")
    print("2. Use ngrok to expose localhost: ngrok http 3000")
    print("3. Set the webhook URL in Twilio WhatsApp to: https://your-ngrok-url.ngrok.io/whatsapp")
    print("4. Message your Twilio WhatsApp number with questions about ASU!")
    
    print("\n📋 WhatsApp Setup Steps:")
    print("1. In Twilio Console, go to Messaging > Try it out > Send a WhatsApp message")
    print("2. Follow the instructions to join your WhatsApp sandbox")
    print("3. Set the webhook URL for incoming messages")
    print("4. Start messaging!")
    
    print("\n✅ Setup complete! Check your .env file and update with your Twilio credentials.")

def create_env_file():
    """Create a basic .env file"""
    env_content = """# OpenAI API (required)
OPENAI_API_KEY=your_openai_key_here

# Reddit API (optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=ASU-RAG-System/1.0

# Twilio SMS Configuration (optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    main() 