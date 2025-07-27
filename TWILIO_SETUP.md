# Twilio SMS & WhatsApp Setup Guide

This guide will help you set up Twilio for both SMS and WhatsApp functionality with your ASU RAG System.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Make sure you're in your virtual environment
source venv/bin/activate

# Install Twilio (if not already installed)
pip install twilio
```

### 2. Get Twilio Credentials

1. **Sign up for Twilio** at https://www.twilio.com
2. **Get your Account SID and Auth Token** from the Twilio Console
3. **Get a Twilio phone number** (for SMS)
4. **Set up WhatsApp** (see WhatsApp section below)

### 3. Configure Environment Variables

Add these to your `.env` file:
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
```

### 4. Start the Server
```bash
python3 main.py --serve --sms
```

## 📱 SMS Setup

### 1. Configure SMS Webhook
1. Go to Twilio Console > Phone Numbers > Manage > Active numbers
2. Click on your phone number
3. Under "Messaging", set the webhook URL to:
   ```
   https://your-domain.com/sms
   ```
4. Set HTTP method to POST

### 2. Test SMS
1. Use ngrok to expose your local server:
   ```bash
   ngrok http 3000
   ```
2. Update the webhook URL in Twilio with your ngrok URL:
   ```
   https://your-ngrok-url.ngrok.io/sms
   ```
3. Text your Twilio number with questions about ASU!

## 💬 WhatsApp Setup

### 1. Enable WhatsApp in Twilio
1. Go to Twilio Console > Messaging > Try it out > Send a WhatsApp message
2. Follow the instructions to join your WhatsApp sandbox
3. You'll get a WhatsApp number like `+14155238886`

### 2. Configure WhatsApp Webhook
1. In the WhatsApp sandbox settings, set the webhook URL to:
   ```
   https://your-domain.com/whatsapp
   ```
2. Set HTTP method to POST

### 3. Test WhatsApp
1. Use ngrok to expose your local server:
   ```bash
   ngrok http 3000
   ```
2. Update the webhook URL with your ngrok URL:
   ```
   https://your-ngrok-url.ngrok.io/whatsapp
   ```
3. Message your Twilio WhatsApp number with questions about ASU!

## 🔧 API Endpoints

### SMS Endpoints
- `POST /sms` - Handle incoming SMS
- `POST /sms/send` - Send SMS manually
- `GET /sms/status` - Check SMS status

### WhatsApp Endpoints
- `POST /whatsapp` - Handle incoming WhatsApp messages
- `POST /whatsapp/send` - Send WhatsApp message manually
- `GET /whatsapp/status` - Check WhatsApp status

## 🧪 Testing

### Test SMS Sending
```bash
curl -X POST http://localhost:3000/sms/send \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890", "message": "Test message"}'
```

### Test WhatsApp Sending
```bash
curl -X POST http://localhost:3000/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890", "message": "Test WhatsApp message"}'
```

### Check Status
```bash
curl http://localhost:3000/sms/status
curl http://localhost:3000/whatsapp/status
```

## 📋 Example Questions

Try these questions via SMS or WhatsApp:
- "What are the admission requirements for ASU?"
- "How many campuses does ASU have?"
- "Tell me about research programs at ASU"
- "What do students say about dorm life?"
- "What are the popular majors at ASU?"

## 🔍 Troubleshooting

### Common Issues

1. **"Twilio credentials not found"**
   - Check your `.env` file has the correct credentials
   - Restart the server after updating `.env`

2. **"SMS functionality not available"**
   - Verify your Twilio credentials are correct
   - Check that your Twilio account is active

3. **Webhook not receiving messages**
   - Ensure ngrok is running and the URL is correct
   - Check that the webhook URL is set correctly in Twilio
   - Verify the server is running on port 3000

4. **WhatsApp not working**
   - Make sure you've joined the WhatsApp sandbox
   - Verify the webhook URL is set for WhatsApp (not SMS)
   - Check that your Twilio number supports WhatsApp

### Debug Mode
To see detailed logs, start the server with debug mode:
```bash
python3 main.py --serve --sms
```

Then check the logs in `asu_rag.log` for detailed information.

## 🎯 Production Deployment

For production use:
1. Use a proper domain instead of ngrok
2. Set up SSL certificates
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up proper logging and monitoring
5. Consider rate limiting for the webhook endpoints

## 📞 Support

If you encounter issues:
1. Check the Twilio documentation
2. Review the server logs in `asu_rag.log`
3. Test the endpoints manually using curl
4. Verify your Twilio account status and billing 