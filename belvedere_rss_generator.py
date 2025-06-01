#!/usr/bin/env python3
"""
City of Belvedere News RSS Feed Generator

This script scrapes the City of Belvedere news page and generates an RSS feed
from the articles found on the page.

Usage:
    python belvedere_rss_generator.py [output_file]

Dependencies:
    pip install requests beautifulsoup4 lxml
"""

import re
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

class BelvedereRSSGenerator:
    def __init__(self):
        self.base_url = "https://www.cityofbelvedere.org"
        self.news_url = "https://www.cityofbelvedere.org/news"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_page(self, url):
        """Fetch the content of a web page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_article_info(self, article_element):
        """Extract title, link, and description from an article element"""
        info = {
            'title': '',
            'link': '',
            'description': '',
            'pub_date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        }
        
        # Try to find title - look for various heading tags and link text
        title_elem = (article_element.find(['h1', 'h2', 'h3', 'h4']) or 
                     article_element.find('a') or
                     article_element.find(class_=re.compile(r'title|headline', re.I)))
        
        if title_elem:
            info['title'] = title_elem.get_text(strip=True)
        
        # Try to find link
        link_elem = article_element.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            info['link'] = urljoin(self.base_url, href)
        
        # Extract description from text content
        # Remove title text from description
        full_text = article_element.get_text(separator=' ', strip=True)
        if info['title'] and full_text.startswith(info['title']):
            description = full_text[len(info['title']):].strip()
        else:
            description = full_text
        
        # Limit description length and clean it up
        if len(description) > 500:
            description = description[:500] + "..."
        
        info['description'] = description
        
        return info
    
    def parse_news_page(self, html_content):
        """Parse the news page and extract article information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Look for article containers - try multiple selectors
        article_selectors = [
            'article',
            '.post',
            '.news-item',
            '.entry',
            '[class*="post"]',
            '[class*="article"]',
            '[class*="news"]'
        ]
        
        article_elements = []
        for selector in article_selectors:
            found = soup.select(selector)
            if found:
                article_elements = found
                break
        
        # If no specific article containers found, look for patterns in the content
        if not article_elements:
            # Look for divs or sections that contain links to news articles
            potential_articles = soup.find_all(['div', 'section'], 
                                             string=re.compile(r'.+', re.DOTALL))
            
            # Filter for elements that contain links to news articles
            for elem in potential_articles:
                links = elem.find_all('a', href=True)
                if links and any('/news' in link.get('href', '') or 
                              '/' in link.get('href', '') for link in links):
                    article_elements.append(elem)
        
        # If still no articles found, try to find all links that look like news articles
        if not article_elements:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if ('/news' in href or href.startswith('/')) and link.get_text(strip=True):
                    # Create a pseudo-article element
                    article_elements.append(link.parent or link)
        
        # Extract information from found elements
        seen_links = set()
        for elem in article_elements[:20]:  # Limit to first 20 articles
            try:
                article_info = self.extract_article_info(elem)
                
                # Skip if we don't have essential information or if it's a duplicate
                if (not article_info['title'] or 
                    not article_info['link'] or 
                    article_info['link'] in seen_links):
                    continue
                
                seen_links.add(article_info['link'])
                articles.append(article_info)
                
            except Exception as e:
                print(f"Error processing article element: {e}")
                continue
        
        return articles
    
    def generate_rss(self, articles, output_file=None):
        """Generate RSS feed XML from articles"""
        # Create RSS root element
        rss = ET.Element('rss', version='2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        
        # Create channel
        channel = ET.SubElement(rss, 'channel')
        
        # Add channel metadata
        ET.SubElement(channel, 'title').text = 'City of Belvedere News'
        ET.SubElement(channel, 'link').text = self.news_url
        ET.SubElement(channel, 'description').text = 'Official news and updates from the City of Belvedere, California'
        ET.SubElement(channel, 'language').text = 'en-us'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        ET.SubElement(channel, 'managingEditor').text = 'clerk@cityofbelvedere.org (City of Belvedere)'
        ET.SubElement(channel, 'webMaster').text = 'clerk@cityofbelvedere.org (City of Belvedere)'
        
        # Add atom:link for self-reference
        atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', f"{self.base_url}/rss.xml")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
        
        # Add articles as items
        for article in articles:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = article['title']
            ET.SubElement(item, 'link').text = article['link']
            ET.SubElement(item, 'description').text = article['description']
            ET.SubElement(item, 'pubDate').text = article['pub_date']
            
            # Use link as GUID
            guid = ET.SubElement(item, 'guid')
            guid.set('isPermaLink', 'true')
            guid.text = article['link']
        
        # Generate XML string
        rough_string = ET.tostring(rss, 'unicode')
        
        # Pretty print the XML
        try:
            from xml.dom import minidom
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            # Remove empty lines and fix XML declaration
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            pretty_xml = '\n'.join(lines)
        except:
            # Fallback if minidom fails
            pretty_xml = rough_string
        
        # Save to file or return
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            print(f"RSS feed saved to {output_file}")
        else:
            return pretty_xml
    
    def run(self, output_file=None):
        """Main execution method"""
        print("Fetching Belvedere news page...")
        html_content = self.fetch_page(self.news_url)
        
        if not html_content:
            print("Failed to fetch news page")
            return False
        
        print("Parsing articles...")
        articles = self.parse_news_page(html_content)
        
        if not articles:
            print("No articles found on the page")
            return False
        
        print(f"Found {len(articles)} articles")
        for i, article in enumerate(articles[:5], 1):
            print(f"  {i}. {article['title']}")
        
        if len(articles) > 5:
            print(f"  ... and {len(articles) - 5} more")
        
        print("Generating RSS feed...")
        self.generate_rss(articles, output_file)
        
        return True

def main():
    """Command line interface"""
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'belvedere_news.xml'
    
    generator = BelvedereRSSGenerator()
    success = generator.run(output_file)
    
    if success:
        print(f"\nRSS feed successfully generated!")
        print(f"You can now use '{output_file}' with any RSS reader.")
    else:
        print("Failed to generate RSS feed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
