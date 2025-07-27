import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for ASU RAG System"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ASU-RAG-System/1.0")
    
    # Twilio SMS Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Data Paths
    DATA_DIR = "data"
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")
    ASU_RAW_DIR = os.path.join(RAW_DATA_DIR, "asu_web")
    REDDIT_RAW_DIR = os.path.join(RAW_DATA_DIR, "reddit")
    
    # RAG Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4"
    COLLECTION_NAME = "asu_rag"
    BATCH_SIZE = 100
    
    # Vector Store Configuration
    VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chromadb")  # "chromadb" or "qdrant"
    VECTOR_DB_PATH = VECTOR_DB_DIR  # For ChromaDB (directory path, not file)
    
    # Qdrant Configuration
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 1536))  # OpenAI text-embedding-3-small
    
    # Web Scraping
    USER_AGENT = "ASU-RAG-System/1.0 (Educational Research)"
    DELAY_SEC = 1
    ASU_SITEMAPS = [
        "https://www.asu.edu/sitemap.xml",
        "https://news.asu.edu/sitemap.xml",
        "https://research.asu.edu/sitemap.xml"
    ]
    
    # Reddit Settings - Historical data scraping (like 7-22)
    REDDIT_SUBREDDITS = [
        # Core ASU subreddits (high priority)
        "ASU",
        "ASUEngineering", 
        "ASUOnline",
        "ASUDevils",
        "ASUStudents",
        "ASUAlumni",
        "ASUGradSchool",
        "ASUUndergrad",
        "ASUResearch",
        "ASUInnovation",
        "ASUGlobal",
        "ASUHealth",
        "ASUArts",
        "ASUBusiness",
        "ASULaw",
        "ASUJournalism",
        "ASUDataScience",
        "University"
    ]
    
    # High-performance Reddit scraping settings for powerful computer
    REDDIT_POST_LIMIT = 1000  # Higher limit for comprehensive data
    REDDIT_TIME_FILTERS = ["week", "month", "year"]  # Multiple time periods
    REDDIT_COMMENT_LIMIT = None  # No limit - get all comments
    REDDIT_DELAY = 0.2  # Very fast delay for powerful computer
    REDDIT_MAX_WORKERS = 50  # High worker count for parallel processing
    REDDIT_BATCH_SIZE = 100  # Larger batches for efficiency
    
    # Web Interface
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 3000
    DEBUG = False
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "asu_rag.log"
    
    def validate(self):
        """Validate required configuration"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Vector store validation
        if self.VECTOR_STORE_TYPE == "qdrant":
            if not self.QDRANT_URL or not self.QDRANT_API_KEY:
                raise ValueError("QDRANT_URL and QDRANT_API_KEY are required when using Qdrant vector store")
        
        # Reddit keys are optional but recommended
        if not self.REDDIT_CLIENT_ID or not self.REDDIT_CLIENT_SECRET:
            print("⚠️  Reddit API keys not found. Reddit scraping will be disabled.")
        
        # Twilio keys are optional but required for SMS functionality
        if not all([self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN, self.TWILIO_PHONE_NUMBER]):
            print("⚠️  Twilio API keys not found. SMS functionality will be disabled.") 