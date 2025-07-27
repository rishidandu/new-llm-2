import os
import time
import hashlib
import datetime
import logging
from typing import List, Optional
from dataclasses import dataclass, asdict
import json

import praw
from tqdm import tqdm

from config.settings import Config

@dataclass
class RedditPost:
    """Represents a Reddit post with metadata"""
    id: str
    title: str
    content: str
    author: str
    subreddit: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    scraped_at: str
    post_type: str  # 'submission' or 'comment'
    parent_id: Optional[str] = None

class RedditScraper:
    """Scrapes Reddit data from ASU-related subreddits"""
    
    def __init__(self, config: Config):
        self.config = config
        # Setup logging first
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Reddit client if credentials are available
        if config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_CLIENT_SECRET,
                user_agent=config.REDDIT_USER_AGENT
            )
        else:
            self.reddit = None
            self.logger.warning("Reddit credentials not found. Reddit scraping disabled.")
        
        # Validate subreddits
        self.valid_subreddits = []
        if self.reddit:
            self._validate_subreddits()
    
    def _validate_subreddits(self):
        """Validate which subreddits exist and are accessible"""
        self.logger.info("Validating subreddits...")
        
        for subreddit_name in self.config.REDDIT_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                # Try to access the subreddit
                _ = subreddit.display_name
                self.valid_subreddits.append(subreddit_name)
                self.logger.info(f"✅ {subreddit_name} - Valid")
            except Exception as e:
                self.logger.warning(f"❌ {subreddit_name} - Invalid: {e}")
        
        self.logger.info(f"Found {len(self.valid_subreddits)} valid subreddits")
    
    def scrape_subreddit(self, subreddit_name: str, limit: int = 100, time_filter: str = 'week') -> List[RedditPost]:
        """Scrape posts from a specific subreddit"""
        posts = []
        
        if not self.reddit:
            self.logger.warning("Reddit client not initialized. Skipping scraping.")
            return posts
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Try different sorting methods to get more content
            sorting_methods = ['top', 'hot', 'new']
            
            for sort_method in sorting_methods:
                try:
                    if sort_method == 'top':
                        submissions = subreddit.top(time_filter=time_filter, limit=limit//len(sorting_methods))
                    elif sort_method == 'hot':
                        submissions = subreddit.hot(limit=limit//len(sorting_methods))
                    elif sort_method == 'new':
                        submissions = subreddit.new(limit=limit//len(sorting_methods))
                    
                    for submission in submissions:
                        try:
                            # Create post object
                            post = RedditPost(
                                id=submission.id,
                                title=submission.title,
                                content=submission.selftext or "",
                                author=str(submission.author) if submission.author else "[deleted]",
                                subreddit=subreddit_name,
                                url=f"https://reddit.com{submission.permalink}",
                                score=submission.score,
                                num_comments=submission.num_comments,
                                created_utc=submission.created_utc,
                                scraped_at=datetime.datetime.utcnow().isoformat() + "Z",
                                post_type="submission"
                            )
                            posts.append(post)
                            
                            # Scrape top comments
                            if submission.num_comments > 0:
                                submission.comments.replace_more(limit=0)
                                for comment in submission.comments.list()[:self.config.REDDIT_COMMENT_LIMIT]:
                                    if comment.body and len(comment.body.strip()) > 30:  # Reduced minimum length
                                        comment_post = RedditPost(
                                            id=comment.id,
                                            title=f"Comment on: {submission.title}",
                                            content=comment.body,
                                            author=str(comment.author) if comment.author else "[deleted]",
                                            subreddit=subreddit_name,
                                            url=f"https://reddit.com{comment.permalink}",
                                            score=comment.score,
                                            num_comments=0,
                                            created_utc=comment.created_utc,
                                            scraped_at=datetime.datetime.utcnow().isoformat() + "Z",
                                            post_type="comment",
                                            parent_id=submission.id
                                        )
                                        posts.append(comment_post)
                            
                            time.sleep(self.config.REDDIT_DELAY)  # Rate limiting
                            
                        except Exception as e:
                            self.logger.error(f"Error scraping submission {submission.id}: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Error with {sort_method} sorting for r/{subreddit_name}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping subreddit r/{subreddit_name}: {e}")
        
        return posts
    
    def scrape_all(self, limit: int = None, time_filters: List[str] = None):
        """Scrape all valid subreddits with multiple time filters"""
        all_posts = []
        
        if not self.reddit:
            self.logger.warning("Reddit client not initialized. Skipping scraping.")
            return None
        
        # Use config defaults if not specified
        if limit is None:
            limit = self.config.REDDIT_POST_LIMIT
        if time_filters is None:
            time_filters = self.config.REDDIT_TIME_FILTERS
        
        self.logger.info(f"Starting comprehensive scrape of {len(self.valid_subreddits)} subreddits...")
        self.logger.info(f"Using time filters: {time_filters}")
        self.logger.info(f"Post limit per subreddit: {limit}")
        
        for subreddit_name in self.valid_subreddits:
            self.logger.info(f"Scraping r/{subreddit_name}...")
            subreddit_posts = []
            
            # Scrape with different time filters
            for time_filter in time_filters:
                self.logger.info(f"  - Scraping {time_filter} posts...")
                posts = self.scrape_subreddit(subreddit_name, limit//len(time_filters), time_filter)
                subreddit_posts.extend(posts)
                time.sleep(self.config.REDDIT_DELAY * 2)  # Extra delay between time filters
            
            # Remove duplicates based on post ID
            unique_posts = {post.id: post for post in subreddit_posts}.values()
            all_posts.extend(unique_posts)
            
            self.logger.info(f"  - Collected {len(unique_posts)} unique posts from r/{subreddit_name}")
            time.sleep(self.config.REDDIT_DELAY * 3)  # Rate limiting between subreddits
        
        self.logger.info(f"Scraped {len(all_posts)} total unique posts/comments")
        
        # Save to JSONL
        os.makedirs(self.config.REDDIT_RAW_DIR, exist_ok=True)
        today = datetime.date.today()
        filename = f"{self.config.REDDIT_RAW_DIR}/{today}.jsonl"
        
        with open(filename, 'w', encoding='utf-8') as f:
            for post in all_posts:
                # Create RAG-compatible record
                rag_record = {
                    "id": hashlib.sha256(post.url.encode()).hexdigest(),
                    "url": post.url,
                    "title": post.title,
                    "ingested_at": post.scraped_at,
                    "text": post.content,
                    "html": f"<h1>{post.title}</h1><p>{post.content}</p>",
                    "metadata": {
                        "source": "reddit",
                        "subreddit": post.subreddit,
                        "author": post.author,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "post_type": post.post_type,
                        "parent_id": post.parent_id,
                        "reddit_id": post.id
                    }
                }
                f.write(json.dumps(rag_record) + '\n')
        
        self.logger.info(f"Saved {len(all_posts)} posts to {filename}")
        return filename

def main():
    """Main function for running the scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ASU Reddit Scraper")
    parser.add_argument("--limit", type=int, default=None, help="Number of posts per subreddit")
    parser.add_argument("--time-filters", nargs="+", default=None, help="Time filters to use")
    parser.add_argument("--schedule", action="store_true", help="Run as a scheduled job")
    
    args = parser.parse_args()
    
    config = Config()
    scraper = RedditScraper(config)
    
    if args.schedule:
        # Run as scheduled job (e.g., nightly)
        import schedule
        import time as time_module
        
        def job():
            print("🔄 Running scheduled Reddit scrape...")
            scraper.scrape_all()
            print("✅ Scheduled scrape completed!")
        
        schedule.every().day.at("02:00").do(job)  # Run at 2 AM
        
        print(" Starting scheduled Reddit scraper...")
        while True:
            schedule.run_pending()
            time_module.sleep(60)
    else:
        # Run once
        print("🔄 Starting Reddit scrape...")
        scraper.scrape_all(args.limit, args.time_filters)
        print("✅ Reddit scrape completed!")

if __name__ == "__main__":
    main() 