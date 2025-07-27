# 🚀 Production Deployment Guide

## Overview
This guide covers deploying the ASU RAG API to production with proper security, monitoring, and scalability.

## ✅ Prerequisites

1. **Domain & SSL Certificate**
   - Purchase a domain (e.g., `yourdomain.com`)
   - Obtain SSL certificate (Let's Encrypt is free)
   - Configure DNS to point to your server

2. **Server Requirements**
   - Ubuntu 20.04+ or similar Linux distribution
   - 4GB+ RAM (8GB recommended for RAG operations)
   - 50GB+ storage
   - Python 3.9+

3. **External Services**
   - OpenAI API key (production tier)
   - Twilio account with WhatsApp Business API access
   - Vector database (optional: Pinecone, Weaviate for scale)

## 🔧 Step-by-Step Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash asurag
sudo usermod -aG sudo asurag
```

### 2. Application Deployment

```bash
# Switch to application user
sudo su - asurag

# Clone repository
git clone https://github.com/yourusername/PagerLifeLLM.git
cd PagerLifeLLM

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements-prod.txt
```

### 3. Environment Configuration

```bash
# Create production .env file
cat > .env << EOF
OPENAI_API_KEY=your_production_openai_key
TWILIO_ACCOUNT_SID=your_production_twilio_sid
TWILIO_AUTH_TOKEN=your_production_twilio_token
TWILIO_PHONE_NUMBER=your_production_whatsapp_number
FLASK_ENV=production
EOF
```

### 4. Nginx Configuration

```bash
# Create Nginx config
sudo tee /etc/nginx/sites-available/asu-rag << EOF
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/asu-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. Systemd Service

```bash
# Create systemd service
sudo tee /etc/systemd/system/asu-rag.service << EOF
[Unit]
Description=ASU RAG API
After=network.target

[Service]
Type=exec
User=asurag
Group=asurag
WorkingDirectory=/home/asurag/PagerLifeLLM
Environment=PATH=/home/asurag/PagerLifeLLM/venv/bin
ExecStart=/home/asurag/PagerLifeLLM/venv/bin/gunicorn --config gunicorn.conf.py src.rag.api_server:create_api_server()
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable asu-rag
sudo systemctl start asu-rag
```

### 7. Update Twilio Webhook

1. Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox
2. Update webhook URL to: `https://yourdomain.com/webhook/whatsapp`
3. Set HTTP method to POST

## 🔒 Security Considerations

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Rate Limiting

The application includes Flask-Limiter for rate limiting. Configure in `src/rag/api_server.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 3. Environment Security

```bash
# Secure .env file
chmod 600 .env
chown asurag:asurag .env
```

## 📊 Monitoring & Logging

### 1. Log Management

```bash
# View application logs
sudo journalctl -u asu-rag -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Health Checks

```bash
# Test health endpoint
curl https://yourdomain.com/health

# Test WhatsApp webhook
curl -X POST https://yourdomain.com/webhook/whatsapp \
  -d "Body=test&From=whatsapp:+1234567890" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

## 🔄 Updates & Maintenance

### 1. Application Updates

```bash
# Pull latest changes
cd /home/asurag/PagerLifeLLM
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements-prod.txt

# Restart service
sudo systemctl restart asu-rag
```

### 2. Database Maintenance

```bash
# Backup ChromaDB data
tar -czf backup-$(date +%Y%m%d).tar.gz data/vector_db/

# Monitor disk usage
df -h
du -sh data/vector_db/
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo systemctl status asu-rag
   sudo journalctl -u asu-rag -n 50
   ```

2. **Memory issues**
   ```bash
   # Monitor memory usage
   free -h
   ps aux | grep gunicorn
   ```

3. **Webhook not working**
   - Check SSL certificate validity
   - Verify Twilio webhook URL
   - Check firewall settings

### Performance Optimization

1. **Increase workers** in `gunicorn.conf.py`
2. **Add Redis** for session management
3. **Use CDN** for static assets
4. **Implement caching** for frequent queries

## 📈 Scaling Considerations

1. **Load Balancer**: Use multiple application servers
2. **Database**: Migrate to managed vector database
3. **Caching**: Implement Redis for response caching
4. **CDN**: Use CloudFlare or similar for global distribution

## 🎯 Production Checklist

- [ ] Domain and SSL configured
- [ ] Environment variables set
- [ ] Nginx configured and tested
- [ ] Systemd service running
- [ ] Twilio webhook updated
- [ ] Firewall configured
- [ ] Monitoring in place
- [ ] Backup strategy implemented
- [ ] Health checks passing
- [ ] Rate limiting configured 