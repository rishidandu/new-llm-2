# ASU RAG System

## 🚀 Features
- **Reddit and ASU Web Scraping** (daily, historical, turbo modes)
- **Efficient Data Deduplication**
- **Context-rich Chunking for RAG**
- **Parallel Embedding Generation**
- **ChromaDB Vector Store Integration**
- **Twilio SMS/WhatsApp Integration**
- **Production-ready, Scalable**

---

## 🗂️ Directory Structure

```
├── data/
│   ├── raw/
│   │   └── reddit/
│   │       ├── 2025-07-24.jsonl                # Daily scrape
│   │       └── historical/2025-07-24.jsonl    # Historical scrape
│   └── processed/
│       └── reddit_combined_2025-07-24.jsonl   # Combined, deduped
│   └── vector_db/chroma.sqlite3               # ChromaDB
├── scripts/
│   ├── turbo_scrape.py
│   ├── smart_scrape.py
│   ├── historical_scrape.py
│   ├── combine_and_embed_reddit.py
│   ├── build_rag_optimized.py
│   └── ...
```

---

## 🧑‍💻 **Scraping Scripts**

### 1. **Turbo Scraping** (max speed, all subreddits)
```bash
python scripts/turbo_scrape.py --workers 50 --limit 1000 --mode both
```
- `--mode daily` for just daily, `--mode historical` for just historical
- `--workers` sets parallelism (use high value for powerful machines)

### 2. **Smart Scraping** (auto-detects what needs to run)
```bash
python scripts/smart_scrape.py --workers 32
```

### 3. **Historical Scraping** (deep, periodic)
```bash
python scripts/historical_scrape.py --workers 20 --limit 1000
```

---

## 🧹 **Combining and Deduplicating Data**

Combine daily and historical Reddit data, deduplicate by `id` (keep latest), and output a single file:

```bash
python scripts/combine_and_embed_reddit.py \
  --daily data/raw/reddit/2025-07-24.jsonl \
  --historical data/raw/reddit/historical/2025-07-24.jsonl \
  --out data/processed/reddit_combined_2025-07-24.jsonl \
  --workers 48
```
- This script will:
  - Combine and deduplicate records
  - Chunk and add conversation context
  - Generate embeddings in parallel (fast!)
  - Store all in ChromaDB

---

## 🧠 **Embedding and Ingestion Pipeline**

- Uses `RAGOptimizedProcessor` for context-rich chunking
- Embeds with OpenAI (parallelized)
- Stores in ChromaDB with all relationships and metadata

**Best Practice:**
- Always deduplicate by `id` before embedding
- Use as many workers as your machine can handle for speed

---

## 🏛️ **ChromaDB Vector Store**
- All embeddings and metadata are stored in `data/vector_db/chroma.sqlite3`
- Metadata includes parent/child/thread relationships for context-aware retrieval

---

## 📞 **Twilio SMS/WhatsApp Integration**
- See `TWILIO_SETUP.md` for setup
- Run `scripts/start_server.py` to launch the web/SMS/WhatsApp interface

---

## 📝 **Example Workflow**

1. **Scrape Reddit (turbo):**
   ```bash
   python scripts/turbo_scrape.py --workers 50 --limit 1000 --mode both
   ```
2. **Combine and embed:**
   ```bash
   python scripts/combine_and_embed_reddit.py \
     --daily data/raw/reddit/2025-07-24.jsonl \
     --historical data/raw/reddit/historical/2025-07-24.jsonl \
     --out data/processed/reddit_combined_2025-07-24.jsonl \
     --workers 48
   ```
3. **Start the server:**
   ```bash
   python scripts/start_server.py
   ```

---

## ⚡ **Tips for Power Users**
- Use high worker counts for scraping and embedding if you have a powerful CPU
- Always deduplicate before embedding to avoid ChromaDB errors and double storage
- For best RAG results, use the combined, context-rich, deduped file as your embedding source

---

## 📚 **More**
- See `SCRAPING_SCHEDULE.md` for cron job automation and advanced scheduling
- See `build_rag_optimized.py` for advanced ingestion with quality scoring and ASU web data 