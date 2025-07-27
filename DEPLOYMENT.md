# Deployment Guide

## Render Deployment

### Prerequisites
- [ ] GitHub repository with your code
- [ ] Render account (free tier available)
- [ ] Environment variables configured

### Quick Deploy to Render

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `rishidandu/new-llm-2`

2. **Configure Service**
   - **Name**: `asu-rag-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements-prod.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT scripts.start_production:main()`

3. **Set Environment Variables**
   ```
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   QDRANT_HOST=your_qdrant_host
   QDRANT_PORT=6333
   QDRANT_API_KEY=your_qdrant_api_key
   FLASK_ENV=production
   PYTHONPATH=.
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Environment Variables Setup

#### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `TWILIO_ACCOUNT_SID`: Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Twilio Auth Token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number

#### Optional Variables
- `QDRANT_HOST`: Qdrant vector database host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `QDRANT_API_KEY`: Qdrant API key (if using cloud)

### Health Check
Your app includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "service": "asu-rag-api"
}
```

### API Endpoints
- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /query` - Query the RAG system
- `POST /webhook/whatsapp` - Twilio WhatsApp webhook
- `POST /webhook/sms` - Twilio SMS webhook

### Troubleshooting

#### Common Issues
1. **Build Failures**: Check that all dependencies are in `requirements-prod.txt`
2. **Startup Failures**: Verify environment variables are set correctly
3. **Health Check Failures**: Check logs for initialization errors

#### Logs
- View logs in Render dashboard under your service
- Production logs are configured with structured logging

### Alternative Deployment

#### Heroku
```bash
# Deploy to Heroku
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set TWILIO_ACCOUNT_SID=your_sid
# ... set other env vars
git push heroku main
```

#### Local Production Testing
```bash
# Test production setup locally
export FLASK_ENV=production
export PORT=8000
python scripts/start_production.py
```

### Security Notes
- ✅ All secrets are environment variables (not in code)
- ✅ Health check endpoint for monitoring
- ✅ Production logging configured
- ✅ CORS enabled for frontend integration
- ✅ Rate limiting ready (flask-limiter included)

### Performance
- Lazy loading of RAG system for faster startup
- Gunicorn for production WSGI server
- Optimized for Render's free tier constraints 