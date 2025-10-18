"""
Simple News Harvest Module
Replaces the missing news-harvest package
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import time

class NewsHarvest:
    """Simple news harvesting implementation"""
    
    def __init__(self):
        self.sources = [
            'https://cointelegraph.com/rss',
            'https://coindesk.com/arc/outboundfeeds/rss/?outputType=xml',
            'https://www.coinbureau.com/feed/',
        ]
    
    def get_news(self, limit=10):
        """Get news from various sources"""
        news_items = []
        
        for source in self.sources:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:limit//len(self.sources)]:
                    news_items.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'source': source
                    })
            except Exception as e:
                print(f"Error fetching from {source}: {e}")
        
        return news_items[:limit]
    
    def search_news(self, query, limit=5):
        """Search for news containing specific query"""
        all_news = self.get_news(limit * 2)
        filtered_news = []
        
        for item in all_news:
            if query.lower() in item['title'].lower() or query.lower() in item['summary'].lower():
                filtered_news.append(item)
                if len(filtered_news) >= limit:
                    break
        
        return filtered_news