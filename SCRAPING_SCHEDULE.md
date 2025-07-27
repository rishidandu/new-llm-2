# Reddit Scraping Schedule Guide

## 🎯 **Recommended Scraping Strategy**

### **1. Daily Fast Scraping**
- **Purpose**: Get recent, fresh content
- **Frequency**: Daily (or multiple times per day)
- **Data**: Recent posts and comments
- **File**: `data/raw/reddit/YYYY-MM-DD.jsonl`
- **Time**: ~30-60 minutes

### **2. Weekly Historical Scraping**
- **Purpose**: Get comprehensive historical data
- **Frequency**: Weekly
- **Data**: Deep historical content with full conversation trees
- **File**: `data/raw/reddit/historical/YYYY-MM-DD.jsonl`
- **Time**: ~2-4 hours

## 🚀 **Automated Scraping Setup**

### **Option 1: Smart Scraping (Recommended)**
```bash
# Run smart scraping (automatically decides what's needed)
python scripts/smart_scrape.py --workers 16

# Force daily scraping only
python scripts/smart_scrape.py --daily-only --workers 16

# Force historical scraping only
python scripts/smart_scrape.py --historical-only --workers 16
```

### **Option 2: Manual Control**
```bash
# Daily fast scraping
python scripts/fast_scrape.py --mode full --workers 16

# Historical scraping
python scripts/historical_scrape.py --workers 8
```

## ⏰ **Cron Job Setup**

### **1. Edit Crontab**
```bash
crontab -e
```

### **2. Add Scraping Jobs**

#### **Daily Scraping (Every Day at 6 AM)**
```bash
0 6 * * * cd /Users/rishidandu/Desktop/pagerlife && source venv/bin/activate && python scripts/smart_scrape.py --daily-only --workers 16 >> /Users/rishidandu/Desktop/pagerlife/scraping.log 2>&1
```

#### **Weekly Historical Scraping (Every Sunday at 2 AM)**
```bash
0 2 * * 0 cd /Users/rishidandu/Desktop/pagerlife && source venv/bin/activate && python scripts/smart_scrape.py --historical-only --workers 8 >> /Users/rishidandu/Desktop/pagerlife/historical_scraping.log 2>&1
```

#### **Smart Scraping (Every Day at 6 AM - Recommended)**
```bash
0 6 * * * cd /Users/rishidandu/Desktop/pagerlife && source venv/bin/activate && python scripts/smart_scrape.py --workers 16 >> /Users/rishidandu/Desktop/pagerlife/smart_scraping.log 2>&1
```

### **3. Multiple Daily Scrapes**
```bash
# Morning scrape
0 6 * * * cd /Users/rishidandu/Desktop/pagerlife && source venv/bin/activate && python scripts/smart_scrape.py --daily-only --workers 16 >> /Users/rishidandu/Desktop/pagerlife/scraping_morning.log 2>&1

# Evening scrape
0 18 * * * cd /Users/rishidud/Desktop/pagerlife && source venv/bin/activate && python scripts/smart_scrape.py --daily-only --workers 16 >> /Users/rishidud/Desktop/pagerlife/scraping_evening.log 2>&1
```

## 📊 **Data Organization**

### **Directory Structure**
```
data/raw/reddit/
├── 2025-07-24.jsonl          # Daily data (today)
├── 2025-07-23.jsonl          # Daily data (yesterday)
├── 2025-07-22.jsonl          # Daily data (older)
└── historical/
    ├── 2025-07-21.jsonl      # Historical data (weekly)
    └── 2025-07-14.jsonl      # Historical data (older)
```

### **File Sizes**
- **Daily files**: ~5-10 MB (30-60 minutes)
- **Historical files**: ~50-100 MB (2-4 hours)

## 🔧 **Monitoring and Maintenance**

### **1. Check Scraping Logs**
```bash
# View recent scraping activity
tail -50 /Users/rishidud/Desktop/pagerlife/smart_scraping.log

# Check for errors
grep -i error /Users/rishidud/Desktop/pagerlife/smart_scraping.log
```

### **2. Monitor Data Growth**
```bash
# Check data directory sizes
du -sh data/raw/reddit/
du -sh data/raw/reddit/historical/

# Count files
ls -1 data/raw/reddit/*.jsonl | wc -l
ls -1 data/raw/reddit/historical/*.jsonl | wc -l
```

### **3. Cleanup Old Data**
```bash
# Keep last 30 days of daily data
find data/raw/reddit/ -name "*.jsonl" -mtime +30 -delete

# Keep last 4 weeks of historical data
find data/raw/reddit/historical/ -name "*.jsonl" -mtime +28 -delete
```

## 🎯 **Performance Optimization**

### **1. Worker Counts**
- **Daily scraping**: 16 workers (faster, less comprehensive)
- **Historical scraping**: 8 workers (slower, more comprehensive)

### **2. Time Windows**
- **Daily**: Run during low-traffic hours (6 AM, 6 PM)
- **Historical**: Run during off-peak (2 AM Sunday)

### **3. Resource Management**
- **Memory**: Historical scraping uses more memory
- **CPU**: Both use significant CPU during processing
- **Network**: Reddit API rate limits apply

## 🚨 **Troubleshooting**

### **Common Issues**
1. **Rate limiting**: Reduce worker count
2. **Memory errors**: Use fewer workers for historical scraping
3. **Network timeouts**: Check internet connection
4. **Permission errors**: Ensure script is executable

### **Emergency Commands**
```bash
# Stop all scraping
pkill -f "python.*scrape"

# Check running processes
ps aux | grep scrape

# Force rebuild RAG system
python scripts/build_rag_optimized.py
``` 