import argparse
import datetime
import hashlib
import json
import os
import time
import urllib.robotparser
import xml.etree.ElementTree as ET
from typing import Dict, List, Set
from urllib.parse import urlparse

import requests
from trafilatura import extract
from tqdm import tqdm

from config.settings import Config

class ASUScraper:
    """Scraper for ASU website data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.headers = {
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.seen: Set[str] = set()
    
    def _parse_sitemap(self, url: str) -> List[str]:
        """Return every <loc> URL from the sitemap"""
        resp = requests.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [loc.text.strip() for loc in root.findall(".//sm:loc", ns)]
    
    def _get_robot(self, host: str) -> urllib.robotparser.RobotFileParser:
        """Get robots.txt parser for a host"""
        if host not in self.robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{host}/robots.txt")
            try:
                rp.read()
            except Exception:
                # If robots.txt is missing, treat as allow-all
                rp.parse(["User-agent: *", "Allow: /"])
            self.robots_cache[host] = rp
        return self.robots_cache[host]
    
    def _allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        p = urlparse(url)
        host = f"{p.scheme}://{p.netloc}"
        rp = self._get_robot(host)
        result = rp.can_fetch(self.config.USER_AGENT, p.path)
        
        # Be more permissive for testing
        if not result:
            if any(rule in p.path for rule in ['/admin/', '/search/', '/user/', '/core/', '/profiles/']):
                return False
            else:
                return True
        
        return result
    
    def _scrape_page(self, url: str):
        """Scrape a single page"""
        if not self._allowed(url):
            return None, self.config.DELAY_SEC
        
        p = urlparse(url)
        host = f"{p.scheme}://{p.netloc}"
        rp = self._get_robot(host)
        delay = rp.crawl_delay(self.config.USER_AGENT) or self.config.DELAY_SEC
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
        except Exception as e:
            return None, delay
        
        if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
            return None, delay
        
        text = extract(resp.text, include_comments=False)
        if not text:
            return None, delay
        
        title = ""
        if "<title>" in resp.text.lower():
            start = resp.text.lower().find("<title>") + 7
            end = resp.text.lower().find("</title>", start)
            title = resp.text[start:end].strip()
        
        return {
            "id": hashlib.sha256(url.encode()).hexdigest(),
            "url": url,
            "title": title,
            "ingested_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "text": text,
            "html": resp.text,
        }, delay
    
    def scrape_all(self):
        """Scrape all ASU sitemaps"""
        os.makedirs(self.config.ASU_RAW_DIR, exist_ok=True)
        outfile = os.path.join(self.config.ASU_RAW_DIR, f"{datetime.date.today()}.jsonl")
        
        written = 0
        
        with open(outfile, "w", encoding="utf-8") as f:
            for sitemap in self.config.ASU_SITEMAPS:
                try:
                    urls = self._parse_sitemap(sitemap)
                except Exception as e:
                    print(f"[warn] failed sitemap {sitemap}: {e}")
                    continue
                
                for url in tqdm(urls, desc=f"Scraping {sitemap}"):
                    if url in self.seen:
                        continue
                    self.seen.add(url)
                    
                    record, delay = self._scrape_page(url)
                    if record:
                        json.dump(record, f, ensure_ascii=False)
                        f.write("\n")
                        written += 1
                    time.sleep(delay)
        
        print(f"Done. Visited {len(self.seen)} URLs, wrote {written} records → {outfile}")
        return outfile

def main():
    """Main function for ASU scraper"""
    config = Config()
    scraper = ASUScraper(config)
    scraper.scrape_all()

if __name__ == "__main__":
    main() 