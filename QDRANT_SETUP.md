# Qdrant Cloud Integration Setup

This guide will help you set up Qdrant Cloud as your vector database for the ASU RAG system, replacing the local ChromaDB with a cloud-based solution.

## 🌟 Benefits of Qdrant Cloud

- **Scalability**: Handle millions of vectors with ease
- **Performance**: Faster search with optimized indexing
- **Reliability**: Cloud-hosted with automatic backups
- **Multi-tenancy**: Separate collections for different use cases
- **API Access**: RESTful API for integration with other services

## 📋 Prerequisites

1. **Qdrant Cloud Account**: Sign up at [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. **Python Dependencies**: Ensure you have the latest requirements installed
3. **Existing ChromaDB Data**: (Optional) If you want to migrate existing data

## 🚀 Quick Setup

### 1. Create Qdrant Cloud Cluster

1. **Sign up** at [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. **Create a new cluster**:
   - Choose your preferred region
   - Select cluster size based on your data volume
   - Note down the cluster URL
3. **Get API credentials**:
   - Go to cluster details
   - Copy the **Cluster URL** (e.g., `https://your-cluster.qdrant.tech`)
   - Copy the **API Key**

### 2. Configure Environment Variables

Add these variables to your `.env` file:

```bash
# Vector Store Configuration
VECTOR_STORE_TYPE=qdrant

# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.tech
QDRANT_API_KEY=your-api-key-here
EMBEDDING_DIM=1536
```

### 3. Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Install the new dependencies
pip install -r requirements.txt
```

### 4. Test Connection

```bash
# Test your Qdrant connection
python scripts/test_qdrant_connection.py
```

Expected output:
```
🚀 Starting Qdrant Cloud connection test...
🔍 Verifying environment variables...
✅ QDRANT_URL: https://your-cluster.qdrant.tech
✅ QDRANT_API_KEY: your-key***
🔌 Testing Qdrant Cloud connection...
✅ Successfully connected to Qdrant Cloud!
🧪 Testing basic operations...
✅ Basic operations test successful!
🎉 All tests passed! Qdrant Cloud is ready to use.
```

## 📦 Migration from ChromaDB

If you have existing data in ChromaDB, use the migration script:

```bash
# Migrate all embeddings from ChromaDB to Qdrant
python scripts/migrate_to_qdrant.py
```

The migration script will:
- ✅ Extract all documents and embeddings from ChromaDB
- ✅ Transfer them to Qdrant Cloud
- ✅ Verify the migration was successful
- ✅ Provide a summary of migrated documents

Expected migration output:
```
🚀 Starting ChromaDB to Qdrant migration...
Connecting to ChromaDB...
Connecting to Qdrant Cloud...
Extracting all documents from ChromaDB...
Found 119007 documents in ChromaDB
Migrating 119007 documents to Qdrant...
✅ Migration verification successful! Document counts match.
🎉 Migration completed successfully!
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `VECTOR_STORE_TYPE` | Vector store backend | `qdrant` or `chromadb` | Yes |
| `QDRANT_URL` | Qdrant cluster URL | `https://xyz.qdrant.tech` | Yes (for Qdrant) |
| `QDRANT_API_KEY` | Qdrant API key | `your-secret-key` | Yes (for Qdrant) |
| `EMBEDDING_DIM` | Embedding dimensions | `1536` (OpenAI default) | No |

### Switching Between Vector Stores

You can easily switch between ChromaDB and Qdrant by changing the `VECTOR_STORE_TYPE` environment variable:

```bash
# Use Qdrant Cloud
VECTOR_STORE_TYPE=qdrant

# Use local ChromaDB
VECTOR_STORE_TYPE=chromadb
```

## 📊 Performance Comparison

| Feature | ChromaDB (Local) | Qdrant Cloud |
|---------|------------------|--------------|
| **Setup** | Simple | Cloud account needed |
| **Scalability** | Limited by disk | Virtually unlimited |
| **Performance** | Good for small datasets | Optimized for large datasets |
| **Backup** | Manual | Automatic |
| **Multi-user** | Single machine | Cloud accessible |
| **Cost** | Free (local storage) | Paid (cloud service) |

## 🔍 Monitoring and Management

### Check Collection Stats

```python
from src.rag.vector_store_factory import create_vector_store

# Create vector store (automatically uses configured type)
store = create_vector_store()

# Get statistics
stats = store.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Collection: {stats['collection_name']}")

# For Qdrant, additional stats are available:
if hasattr(stats, 'vector_size'):
    print(f"Vector dimensions: {stats['vector_size']}")
    print(f"Distance metric: {stats['distance_metric']}")
```

### Qdrant Dashboard

Access your cluster dashboard at [https://cloud.qdrant.io/](https://cloud.qdrant.io/) to:
- Monitor collection metrics
- View search performance
- Manage cluster resources
- Set up alerts

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**
   ```
   ❌ Failed to connect to Qdrant Cloud
   ```
   - Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
   - Check your internet connection
   - Ensure cluster is running

2. **Migration Fails**
   ```
   ❌ Migration verification failed! Document counts don't match.
   ```
   - Check ChromaDB data integrity
   - Verify Qdrant cluster has sufficient storage
   - Try running migration again

3. **Dimension Mismatch**
   ```
   Vector dimension mismatch
   ```
   - Ensure `EMBEDDING_DIM` matches your embedding model
   - OpenAI `text-embedding-3-small` uses 1536 dimensions

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Next Steps

After successful setup:

1. **Test your RAG system** with the new vector store
2. **Monitor performance** in the Qdrant dashboard
3. **Scale your cluster** if needed based on usage
4. **Set up backups** and monitoring alerts
5. **Consider upgrading** ChromaDB references in your code to use the factory pattern

## 🔐 Security Best Practices

1. **Protect API Keys**: Never commit API keys to version control
2. **Use Environment Variables**: Store credentials in `.env` file
3. **Network Security**: Use HTTPS for all connections
4. **Access Control**: Limit API key permissions where possible

## 💡 Tips for Optimal Performance

1. **Batch Operations**: Use batch inserts for better performance
2. **Appropriate Cluster Size**: Start small and scale based on usage
3. **Monitor Metrics**: Watch search latency and throughput
4. **Index Optimization**: Qdrant automatically optimizes indexes

---

## 🎯 Summary

You now have a cloud-based vector store that can:
- ✅ Scale to millions of documents
- ✅ Provide fast similarity search
- ✅ Integrate seamlessly with your existing RAG system
- ✅ Offer cloud reliability and backup

Your ASU RAG system is now ready for production-scale deployment! 🚀 