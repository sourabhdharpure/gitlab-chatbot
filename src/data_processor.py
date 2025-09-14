"""
Data processor for extracting and processing GitLab Handbook and Direction pages.
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib.parse import urljoin, urlparse
import time
from tqdm import tqdm
import re
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebDataProcessor:
    """Processes web pages from any website for chatbot training."""
    
    def __init__(self, base_urls: List[str], max_pages: int = 100):
        """
        Initialize the data processor.
        
        Args:
            base_urls: List of base URLs to scrape
            max_pages: Maximum number of pages to process
        """
        self.base_urls = base_urls
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.processed_urls = set()
        self.documents = []
        
    def extract_text_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract clean text content from HTML soup."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Get text and clean it
            text = main_content.get_text()
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Remove extra newlines
            text = re.sub(r'\n\s*\n', '\n\n', text)
        else:
            text = ""
        
        # Extract headings for structure
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': heading.name,
                'text': heading.get_text().strip()
            })
        
        return {
            'title': title_text,
            'content': text,
            'headings': headings,
            'word_count': len(text.split())
        }
    
    def is_valid_page(self, url: str, content: str) -> bool:
        """Check if the page is valid for processing."""
        # Skip if too short
        if len(content.split()) < 50:
            return False
        
        # Skip non-relevant pages
        skip_patterns = [
            '/careers/', '/jobs/', '/blog/', '/press/',
            '/events/', '/webcast/', '/compare/',
            '.pdf', '.doc', '.xls'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def get_page_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract relevant internal links from the page."""
        from urllib.parse import urlparse
        
        base_domain = urlparse(base_url).netloc
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Only include links from same domain
            if parsed_url.netloc == base_domain:
                # Skip certain file types and common non-content pages
                skip_patterns = [
                    '.pdf', '.doc', '.xls', '.ppt', '.zip', '.tar', '.gz',
                    '/login', '/signup', '/register', '/auth', '/api/',
                    '/admin', '/dashboard', '/profile', '/settings'
                ]
                
                if not any(pattern in full_url.lower() for pattern in skip_patterns):
                    links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def scrape_page(self, url: str) -> Optional[Dict]:
        """Scrape a single page and return structured data."""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_data = self.extract_text_content(soup)
            
            if not self.is_valid_page(url, content_data['content']):
                logger.info(f"Skipping invalid page: {url}")
                return None
            
            # Get internal links for further crawling
            internal_links = self.get_page_links(soup, url)
            
            document = {
                'url': url,
                'title': content_data['title'],
                'content': content_data['content'],
                'headings': content_data['headings'],
                'word_count': content_data['word_count'],
                'internal_links': internal_links,
                'scraped_at': time.time()
            }
            
            return document
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def process_all_pages(self) -> List[Dict]:
        """Process all pages starting from base URLs."""
        urls_to_process = list(self.base_urls)
        processed_count = 0
        
        while urls_to_process and processed_count < self.max_pages:
            current_url = urls_to_process.pop(0)
            
            if current_url in self.processed_urls:
                continue
            
            self.processed_urls.add(current_url)
            document = self.scrape_page(current_url)
            
            if document:
                self.documents.append(document)
                processed_count += 1
                
                # Add new links to process (with limit)
                new_links = [link for link in document['internal_links'] 
                           if link not in self.processed_urls and link not in urls_to_process]
                urls_to_process.extend(new_links[:10])  # Limit new links per page
            
            # Rate limiting
            time.sleep(1)
        
        logger.info(f"Processed {len(self.documents)} documents")
        return self.documents
    
    def chunk_documents(self, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split documents into smaller chunks for better retrieval."""
        chunks = []
        
        for doc in self.documents:
            content = doc['content']
            words = content.split()
            
            if len(words) <= chunk_size:
                # Document is small enough, keep as is
                chunk = doc.copy()
                chunk['chunk_id'] = 0
                chunk['total_chunks'] = 1
                chunks.append(chunk)
            else:
                # Split into chunks
                num_chunks = 0
                for i in range(0, len(words), chunk_size - overlap):
                    chunk_words = words[i:i + chunk_size]
                    chunk_content = ' '.join(chunk_words)
                    
                    chunk = {
                        'url': doc['url'],
                        'title': doc['title'],
                        'content': chunk_content,
                        'headings': doc['headings'],
                        'word_count': len(chunk_words),
                        'chunk_id': num_chunks,
                        'total_chunks': -1,  # Will update after processing
                        'scraped_at': doc['scraped_at']
                    }
                    chunks.append(chunk)
                    num_chunks += 1
                
                # Update total chunks count
                for chunk in chunks[-num_chunks:]:
                    chunk['total_chunks'] = num_chunks
        
        return chunks
    
    def save_data(self, output_dir: str = "data"):
        """Save processed data to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save raw documents
        with open(f"{output_dir}/documents.json", 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        
        # Create and save chunks
        chunks = self.chunk_documents()
        with open(f"{output_dir}/chunks.json", 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        # Create DataFrame for easier analysis
        df = pd.DataFrame(chunks)
        df.to_csv(f"{output_dir}/chunks.csv", index=False)
        
        logger.info(f"Saved {len(self.documents)} documents and {len(chunks)} chunks to {output_dir}/")
        return chunks

def main():
    """Main function to run the data processor."""
    base_urls = [
        "https://about.gitlab.com/handbook/",
        "https://about.gitlab.com/direction/"
    ]
    
    processor = GitLabDataProcessor(base_urls, max_pages=50)
    documents = processor.process_all_pages()
    chunks = processor.save_data()
    
    print(f"✅ Successfully processed {len(documents)} documents")
    print(f"✅ Created {len(chunks)} chunks for training")

if __name__ == "__main__":
    main()
