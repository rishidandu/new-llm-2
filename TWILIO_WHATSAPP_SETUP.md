# 📱 Twilio WhatsApp Setup Guide

## 🚀 Quick Setup for Testing

Your ASU RAG system is now ready for Twilio WhatsApp integration!

### 🌐 Current ngrok URL
```
https://078031fc4e07.ngrok-free.app
```

### 📋 Webhook Endpoints
- **WhatsApp Webhook**: `https://078031fc4e07.ngrok-free.app/webhook/whatsapp`
- **SMS Webhook**: `https://078031fc4e07.ngrok-free.app/webhook/sms`
- **Send WhatsApp**: `https://078031fc4e07.ngrok-free.app/send/whatsapp`
- **Send SMS**: `https://078031fc4e07.ngrok-free.app/send/sms`

## 🔧 Twilio Console Setup

### Step 1: Access Twilio Console
1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**

### Step 2: Configure Webhook
1. In the WhatsApp Sandbox, set the webhook URL to:
   ```
   https://078031fc4e07.ngrok-free.app/webhook/whatsapp
   ```
2. Set HTTP method to **POST**

**🔧 If you're still not getting responses, try the root endpoint:**
   ```
   https://078031fc4e07.ngrok-free.app/
   ```
   (The root endpoint now handles Twilio webhooks automatically)

### Step 3: Test WhatsApp
1. Join your Twilio WhatsApp Sandbox using the provided code
2. Send a message to your Twilio number
3. You should receive a detailed response from the ASU RAG system!

## 🧪 Test Messages to Try

Send these messages to your Twilio WhatsApp number:

### Campus Life
- "What campus jobs are available at ASU?"
- "How do I get a library job?"
- "Tell me about dining options"
- "What's campus life like?"

### Academic
- "MAT 210 course difficulty"
- "Best professors for CS courses"
- "How to find a tutor"

### General
- "Help me find a job"
- "What's the best way to meet people on campus?"
- "Tell me about ASU resources"

## ✅ Expected Responses

Your ASU RAG system will provide:
- **Detailed 4-part answers** (Direct answer, context, next steps, caveats)
- **Reranker-enhanced** document relevance
- **GPT-4 powered** comprehensive responses
- **Real-time processing** with 119,007+ documents

## 🔍 Monitoring

### Check ngrok Status
```bash
# View ngrok dashboard
open http://localhost:4040
```

### Check Server Logs
```bash
# Monitor API server logs
tail -f logs/api_server.log
```

### Test Webhook Manually
```bash
# Test with curl
curl -X POST https://078031fc4e07.ngrok-free.app/webhook/whatsapp \
  -d "Body=What campus jobs are available?&From=+1234567890" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

## 🚨 Important Notes

### ngrok URL Expiration
- **Free ngrok URLs expire** when you restart ngrok
- **Update Twilio webhook** with new URL if needed
- **Consider ngrok paid plan** for persistent URLs

### Production Deployment
For production use:
1. Deploy to a cloud server (AWS, Heroku, etc.)
2. Use HTTPS domain
3. Update Twilio webhook URLs
4. Configure proper logging and monitoring

### Environment Variables
Make sure these are set in your `.env` file:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
OPENAI_API_KEY=your_openai_key
```

## 🎯 Success Indicators

✅ **Working correctly if:**
- You receive detailed, structured responses
- Responses include source citations
- Answer quality is high and relevant
- Response time is under 30 seconds

❌ **Issues to check:**
- ngrok URL is accessible
- Twilio webhook is configured correctly
- API server is running
- Environment variables are set

## 📞 Support

If you encounter issues:
1. Check ngrok dashboard: `http://localhost:4040`
2. Verify API server is running: `http://localhost:3000/health`
3. Test webhook manually with curl
4. Check Twilio console for webhook delivery status

---

**🎉 Your ASU RAG system is now ready for real WhatsApp testing!** 