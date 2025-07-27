import os
import time
import hashlib
import datetime
import logging
import asyncio
import aiohttp
import json
from typing import List, Optional, Dict, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
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
    post_type: str
    parent_id: Optional[str] = None
    depth: Optional[int] = None
    root_submission_id: Optional[str] = None

class FastRedditScraper:
    """Ultra-fast Reddit scraper with parallel processing"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Reddit client
        if config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_CLIENT_SECRET,
                user_agent=config.REDDIT_USER_AGENT
            )
        else:
            self.reddit = None
            self.logger.warning("Reddit credentials not found. Reddit scraping disabled.")
        
        # Optimized settings
        self.max_workers = config.REDDIT_MAX_WORKERS  # Use config setting
        self.batch_size = config.REDDIT_BATCH_SIZE   # Use config setting
        self.optimized_delay = config.REDDIT_DELAY  # Use config setting
        self.seen_posts: Set[str] = set()
        
        # Validate subreddits
        self.valid_subreddits = []
        if self.reddit:
            self._validate_subreddits()
    
    def _validate_subreddits(self):
        """Quick validation of subreddits"""
        self.logger.info("Validating subreddits...")
        
        # Use ThreadPoolExecutor for parallel validation
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_subreddit = {
                executor.submit(self._check_subreddit, subreddit): subreddit 
                for subreddit in self.config.REDDIT_SUBREDDITS
            }
            
            for future in as_completed(future_to_subreddit):
                subreddit = future_to_subreddit[future]
                try:
                    if future.result():
                        self.valid_subreddits.append(subreddit)
                except Exception as e:
                    self.logger.warning(f"❌ {subreddit} - Invalid: {e}")
        
        self.logger.info(f"Found {len(self.valid_subreddits)} valid subreddits")
    
    def _check_subreddit(self, subreddit_name: str) -> bool:
        """Check if a subreddit exists and is accessible"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            _ = subreddit.display_name
            return True
        except:
            return False
    
    def scrape_subreddit_fast(self, subreddit_name: str, limit: int = 100) -> List[RedditPost]:
        """Fast scraping of a single subreddit"""
        posts = []
        
        if not self.reddit:
            return posts
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Use only 'hot' and 'new' for speed (skip 'top' which is slower)
            sorting_methods = ['hot', 'new']
            
            for sort_method in sorting_methods:
                try:
                    if sort_method == 'hot':
                        submissions = subreddit.hot(limit=limit//len(sorting_methods))
                    elif sort_method == 'new':
                        submissions = subreddit.new(limit=limit//len(sorting_methods))
                    
                    for submission in submissions:
                        # Skip if we've already seen this post
                        if submission.id in self.seen_posts:
                            continue
                        
                        self.seen_posts.add(submission.id)
                        
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
                            
                            # Fast comment scraping (only top comments)
                            if submission.num_comments > 0 and len(posts) < limit:
                                submission.comments.replace_more(limit=0)
                                top_comments = submission.comments.list()[:10]  # Reduced comment limit
                                
                                for comment in top_comments:
                                    if comment.body and len(comment.body.strip()) > 20:
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
                            
                            # Minimal delay
                            time.sleep(self.optimized_delay)
                            
                        except Exception as e:
                            self.logger.debug(f"Error with submission {submission.id}: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"Error with {sort_method} for r/{subreddit_name}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping subreddit r/{subreddit_name}: {e}")
        
        return posts
    
    def scrape_all_parallel(self, limit: int = None):
        """Scrape all subreddits in parallel for maximum speed"""
        if not self.reddit:
            self.logger.warning("Reddit client not initialized. Skipping scraping.")
            return None
        
        if limit is None:
            limit = self.config.REDDIT_POST_LIMIT
        
        self.logger.info(f"🚀 Starting parallel scrape of {len(self.valid_subreddits)} subreddits...")
        start_time = time.time()
        
        all_posts = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_subreddit = {
                executor.submit(self.scrape_subreddit_fast, subreddit, limit): subreddit 
                for subreddit in self.valid_subreddits
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=len(self.valid_subreddits), desc="Scraping subreddits") as pbar:
                for future in as_completed(future_to_subreddit):
                    subreddit = future_to_subreddit[future]
                    try:
                        posts = future.result()
                        all_posts.extend(posts)
                        pbar.set_postfix({
                            'subreddit': subreddit,
                            'posts': len(posts),
                            'total': len(all_posts)
                        })
                    except Exception as e:
                        self.logger.error(f"Error scraping r/{subreddit}: {e}")
                    finally:
                        pbar.update(1)
        
        # Remove duplicates
        unique_posts = {post.id: post for post in all_posts}.values()
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"⚡ Scraped {len(unique_posts)} posts in {elapsed_time:.2f} seconds")
        self.logger.info(f"📊 Speed: {len(unique_posts)/elapsed_time:.1f} posts/second")
        
        # Save to JSONL
        return self._save_posts(unique_posts)
    
    def _save_posts(self, posts: List[RedditPost], output_dir: Optional[str] = None) -> str:
        """Save posts to JSONL file"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{output_dir}/{datetime.date.today()}.jsonl"
        else:
            os.makedirs(self.config.REDDIT_RAW_DIR, exist_ok=True)
            filename = f"{self.config.REDDIT_RAW_DIR}/{datetime.date.today()}.jsonl"
        
        with open(filename, 'w', encoding='utf-8') as f:
            for post in posts:
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
        
        self.logger.info(f"💾 Saved {len(posts)} posts to {filename}")
        return filename
    
    def scrape_incremental(self, hours_back: int = 24):
        """Incremental scraping - only get recent posts"""
        if not self.reddit:
            return None
        
        self.logger.info(f"🔄 Starting incremental scrape (last {hours_back} hours)...")
        start_time = time.time()
        
        cutoff_time = time.time() - (hours_back * 3600)
        all_posts = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_subreddit = {
                executor.submit(self._scrape_recent_posts, subreddit, cutoff_time): subreddit 
                for subreddit in self.valid_subreddits
            }
            
            with tqdm(total=len(self.valid_subreddits), desc="Incremental scraping") as pbar:
                for future in as_completed(future_to_subreddit):
                    subreddit = future_to_subreddit[future]
                    try:
                        posts = future.result()
                        all_posts.extend(posts)
                        pbar.set_postfix({
                            'subreddit': subreddit,
                            'new_posts': len(posts)
                        })
                    except Exception as e:
                        self.logger.error(f"Error in incremental scrape r/{subreddit}: {e}")
                    finally:
                        pbar.update(1)
        
        unique_posts = {post.id: post for post in all_posts}.values()
        elapsed_time = time.time() - start_time
        
        self.logger.info(f"🔄 Found {len(unique_posts)} new posts in {elapsed_time:.2f} seconds")
        
        if unique_posts:
            return self._save_posts(unique_posts)
        return None
    
    def _scrape_recent_posts(self, subreddit_name: str, cutoff_time: float) -> List[RedditPost]:
        """Scrape only recent posts from a subreddit"""
        posts = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Only check 'new' posts for incremental scraping
            for submission in subreddit.new(limit=100):
                if submission.created_utc < cutoff_time:
                    break  # Stop if we hit old posts
                
                if submission.id in self.seen_posts:
                    continue
                
                self.seen_posts.add(submission.id)
                
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
                
                time.sleep(self.optimized_delay)
                
        except Exception as e:
            self.logger.debug(f"Error in incremental scrape r/{subreddit_name}: {e}")
        
        return posts

    def scrape_subreddit_full(self, subreddit_name: str, limit: int = 100) -> List[RedditPost]:
        """Scrape all posts and all comments (full tree) from a subreddit"""
        posts = []
        if not self.reddit:
            return posts
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            sorting_methods = ['hot', 'new']
            for sort_method in sorting_methods:
                try:
                    if sort_method == 'hot':
                        submissions = subreddit.hot(limit=limit//len(sorting_methods))
                    elif sort_method == 'new':
                        submissions = subreddit.new(limit=limit//len(sorting_methods))
                    for submission in submissions:
                        if submission.id in self.seen_posts:
                            continue
                        self.seen_posts.add(submission.id)
                        try:
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
                            # Scrape all comments (full tree)
                            submission.comments.replace_more(limit=None)
                            all_comments = submission.comments.list()
                            for comment in all_comments:
                                if comment.id in self.seen_posts:
                                    continue
                                self.seen_posts.add(comment.id)
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
                                    parent_id=comment.parent_id
                                )
                                # Add extra metadata for depth and root
                                comment_post.depth = getattr(comment, 'depth', None)
                                comment_post.root_submission_id = submission.id
                                posts.append(comment_post)
                            time.sleep(self.optimized_delay)
                        except Exception as e:
                            self.logger.debug(f"Error with submission {submission.id}: {e}")
                            continue
                except Exception as e:
                    self.logger.debug(f"Error with {sort_method} for r/{subreddit_name}: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"Error scraping subreddit r/{subreddit_name}: {e}")
        return posts

    def scrape_all_full_parallel(self, limit: int = None):
        """Scrape all subreddits in parallel, full tree (all comments/replies)"""
        if not self.reddit:
            self.logger.warning("Reddit client not initialized. Skipping scraping.")
            return None
        if limit is None:
            limit = self.config.REDDIT_POST_LIMIT
        self.logger.info(f"🚀 Starting FULL parallel scrape of {len(self.valid_subreddits)} subreddits...")
        start_time = time.time()
        all_posts = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_subreddit = {
                executor.submit(self.scrape_subreddit_full, subreddit, limit): subreddit 
                for subreddit in self.valid_subreddits
            }
            with tqdm(total=len(self.valid_subreddits), desc="Full scraping subreddits") as pbar:
                for future in as_completed(future_to_subreddit):
                    subreddit = future_to_subreddit[future]
                    try:
                        posts = future.result()
                        all_posts.extend(posts)
                        pbar.set_postfix({
                            'subreddit': subreddit,
                            'posts': len(posts),
                            'total': len(all_posts)
                        })
                    except Exception as e:
                        self.logger.error(f"Error scraping r/{subreddit}: {e}")
                    finally:
                        pbar.update(1)
        unique_posts = {post.id: post for post in all_posts}.values()
        elapsed_time = time.time() - start_time
        self.logger.info(f"⚡ FULL scrape: {len(unique_posts)} posts in {elapsed_time:.2f} seconds")
        self.logger.info(f"📊 Speed: {len(unique_posts)/elapsed_time:.1f} posts/second")
        return self._save_posts(unique_posts)

    def scrape_all_historical(self, limit: int = 500, time_filters: List[str] = None, sort_methods: List[str] = None, output_dir: str = None):
        """Scrape all subreddits with historical data (like 7-22 approach)"""
        if not self.reddit:
            self.logger.warning("Reddit client not initialized. Skipping scraping.")
            return None
        
        if time_filters is None:
            time_filters = ["week", "month", "year"]
        if sort_methods is None:
            sort_methods = ["hot", "new", "top"]
        
        # Reset seen_posts for historical scraping to get more comprehensive data
        self.seen_posts.clear()
        
        # Use slower delay for historical scraping to avoid rate limits
        original_delay = self.optimized_delay
        self.optimized_delay = 0.3  # Still fast but slightly slower for historical scraping
        
        self.logger.info(f"🏛️ Starting HISTORICAL scrape of {len(self.valid_subreddits)} subreddits...")
        self.logger.info(f"📅 Time filters: {time_filters}")
        self.logger.info(f"📊 Sort methods: {sort_methods}")
        start_time = time.time()
        
        all_posts = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks with historical parameters
            future_to_subreddit = {
                executor.submit(self.scrape_subreddit_historical, subreddit, limit, time_filters, sort_methods): subreddit 
                for subreddit in self.valid_subreddits
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=len(self.valid_subreddits), desc="Historical scraping subreddits") as pbar:
                for future in as_completed(future_to_subreddit):
                    subreddit = future_to_subreddit[future]
                    try:
                        posts = future.result()
                        all_posts.extend(posts)
                        pbar.set_postfix({
                            'subreddit': subreddit,
                            'posts': len(posts),
                            'total': len(all_posts)
                        })
                    except Exception as e:
                        self.logger.error(f"Error scraping r/{subreddit}: {e}")
                    finally:
                        pbar.update(1)
        
        # Remove duplicates
        unique_posts = {post.id: post for post in all_posts}.values()
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"🏛️ HISTORICAL scrape: {len(unique_posts)} posts in {elapsed_time:.2f} seconds")
        self.logger.info(f"📊 Speed: {len(unique_posts)/elapsed_time:.1f} posts/second")
        
        # Restore original delay
        self.optimized_delay = original_delay
        
        # Save to JSONL with custom directory if specified
        return self._save_posts(unique_posts, output_dir)
    
    def scrape_subreddit_historical(self, subreddit_name: str, limit: int = 500, 
                                  time_filters: List[str] = None, sort_methods: List[str] = None) -> List[RedditPost]:
        """Scrape historical posts from a subreddit (like 7-22 approach)"""
        posts = []
        if not self.reddit:
            return posts
        
        if time_filters is None:
            time_filters = ["week", "month", "year"]
        if sort_methods is None:
            sort_methods = ["hot", "new", "top"]
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Try multiple sorting methods and time filters
            for sort_method in sort_methods:
                try:
                    if sort_method == "top":
                        # For "top", try multiple time filters
                        for time_filter in time_filters:
                            try:
                                # Use higher limit for historical scraping
                                submissions = getattr(subreddit, sort_method)(time_filter=time_filter, limit=limit)
                                for submission in submissions:
                                    if submission.id in self.seen_posts:
                                        continue
                                    self.seen_posts.add(submission.id)
                                    
                                    # Create post record
                                    post = RedditPost(
                                        id=submission.id,
                                        title=submission.title,
                                        content=submission.selftext if submission.selftext else submission.title,
                                        author=str(submission.author) if submission.author else "[deleted]",
                                        subreddit=subreddit_name,
                                        url=f"https://reddit.com{submission.permalink}",
                                        score=submission.score,
                                        num_comments=submission.num_comments,
                                        created_utc=submission.created_utc,
                                        scraped_at=datetime.datetime.utcnow().isoformat() + "Z",
                                        post_type="submission",
                                        parent_id=None
                                    )
                                    posts.append(post)
                                    
                                    # Scrape ALL comments (full tree) - more aggressive
                                    try:
                                        submission.comments.replace_more(limit=None)
                                        all_comments = submission.comments.list()
                                        for comment in all_comments:
                                            if comment.id in self.seen_posts:
                                                continue
                                            self.seen_posts.add(comment.id)
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
                                                parent_id=comment.parent_id
                                            )
                                            # Add extra metadata for depth and root
                                            comment_post.depth = getattr(comment, 'depth', None)
                                            comment_post.root_submission_id = submission.id
                                            posts.append(comment_post)
                                    except Exception as comment_error:
                                        self.logger.debug(f"Error getting comments for {submission.id}: {comment_error}")
                                    
                                    time.sleep(self.optimized_delay)
                                    
                            except Exception as e:
                                self.logger.debug(f"Error with {sort_method}/{time_filter} for r/{subreddit_name}: {e}")
                                continue
                    else:
                        # For "hot" and "new", use higher limits for historical scraping
                        submissions = getattr(subreddit, sort_method)(limit=limit)
                        for submission in submissions:
                            if submission.id in self.seen_posts:
                                continue
                            self.seen_posts.add(submission.id)
                            
                            # Create post record
                            post = RedditPost(
                                id=submission.id,
                                title=submission.title,
                                content=submission.selftext if submission.selftext else submission.title,
                                author=str(submission.author) if submission.author else "[deleted]",
                                subreddit=subreddit_name,
                                url=f"https://reddit.com{submission.permalink}",
                                score=submission.score,
                                num_comments=submission.num_comments,
                                created_utc=submission.created_utc,
                                scraped_at=datetime.datetime.utcnow().isoformat() + "Z",
                                post_type="submission",
                                parent_id=None
                            )
                            posts.append(post)
                            
                            # Scrape ALL comments (full tree) - more aggressive
                            try:
                                submission.comments.replace_more(limit=None)
                                all_comments = submission.comments.list()
                                for comment in all_comments:
                                    if comment.id in self.seen_posts:
                                        continue
                                    self.seen_posts.add(comment.id)
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
                                        parent_id=comment.parent_id
                                    )
                                    # Add extra metadata for depth and root
                                    comment_post.depth = getattr(comment, 'depth', None)
                                    comment_post.root_submission_id = submission.id
                                    posts.append(comment_post)
                            except Exception as comment_error:
                                self.logger.debug(f"Error getting comments for {submission.id}: {comment_error}")
                            
                            time.sleep(self.optimized_delay)
                            
                except Exception as e:
                    self.logger.debug(f"Error with {sort_method} for r/{subreddit_name}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping subreddit r/{subreddit_name}: {e}")
        
        return posts

def main():
    """Main function for running the fast scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fast ASU Reddit Scraper")
    parser.add_argument("--limit", type=int, default=None, help="Number of posts per subreddit")
    parser.add_argument("--incremental", type=int, default=None, help="Incremental scrape (hours back)")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    config = Config()
    scraper = FastRedditScraper(config)
    scraper.max_workers = args.workers
    
    if args.incremental:
        print(f"🔄 Starting incremental scrape (last {args.incremental} hours)...")
        scraper.scrape_incremental(args.incremental)
    else:
        print("🚀 Starting fast parallel scrape...")
        scraper.scrape_all_parallel(args.limit)
    
    print("✅ Fast scrape completed!")

if __name__ == "__main__":
    main() 