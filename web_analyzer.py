"""
Single-Page Web Analyzer using Regular Expressions
===================================================
Project for Theory of Computation course.
Demonstrates the application of Regular Expressions in web crawling.

Course: Theory of Computation
"""

import re
import csv
import requests
from urllib.parse import urljoin, urlparse
from collections import Counter
from datetime import datetime
import os

# =====================================================
# REGULAR EXPRESSION PATTERNS
# =====================================================

class RegexPatterns:
    """
    Collection of all Regular Expression Patterns used in this module.
    """
    
    # Email Pattern
    EMAIL = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Phone Number Patterns (supports multiple formats)
    PHONE_PATTERNS = [
        r'0[0-9]{1,2}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # Thai format: 0xx-xxx-xxxx
        r'\+66[-.\s]?[0-9]{1,2}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # Thai with +66
        r'\([0-9]{2,3}\)[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # (0xx) xxx-xxxx
        r'[0-9]{3}[-.\s][0-9]{3}[-.\s][0-9]{4}',  # xxx-xxx-xxxx (US format)
        r'\+[0-9]{1,3}[-.\s]?[0-9]{6,12}',  # International format
    ]
    
    # URL Pattern
    URL = r'https?://[a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+(?:/[^\s<>"\']*)?'
    
    # Relative URL Patterns (href and src attributes)
    HREF = r'href=["\']([^"\']+)["\']'
    SRC = r'src=["\']([^"\']+)["\']'
    
    # IP Address Pattern
    IP_ADDRESS = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    
    # HTML Title Pattern
    TITLE = r'<title[^>]*>([^<]+)</title>'
    
    # Meta Description Pattern
    META_DESC = r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']'
    
    # Social Media Links
    SOCIAL_MEDIA = {
        'facebook': r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9.]+',
        'twitter': r'https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+',
        'instagram': r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
        'linkedin': r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[a-zA-Z0-9-]+',
        'youtube': r'https?://(?:www\.)?youtube\.com/(?:@|channel/|user/)[a-zA-Z0-9_-]+',
        'tiktok': r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.]+',
        'line': r'https?://line\.me/[a-zA-Z0-9/]+',
    }


class WebAnalyzer:
    """
    Main class for analyzing web pages.
    
    Workflow:
    1. Receive a URL from the user
    2. Download the HTML content
    3. Use Regular Expressions to extract data
    4. Process and organize the data
    5. Display results and export
    """
    
    def __init__(self, url: str):
        """
        Create a WebAnalyzer object.
        
        Args:
            url: URL of the web page to analyze
        """
        self.url = url
        self.base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.html_content = ""
        self.results = {
            'emails': [],
            'phones': [],
            'urls': [],
            'ip_addresses': [],
            'social_media': {},
            'page_title': '',
            'meta_description': ''
        }
        
    def fetch_page(self) -> bool:
        """
        Download HTML content from the URL.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            print(f"\n🔍 Downloading web page: {self.url}")
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            
            response.encoding = response.apparent_encoding or 'utf-8'
            self.html_content = response.text
            
            print(f"✅ Download successful! Size: {len(self.html_content):,} characters")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading page: {e}")
            return False
    
    def extract_emails(self) -> list:
        """
        Find email addresses in the HTML content.
        
        Returns:
            list: List of unique emails found
        """
        emails = re.findall(RegexPatterns.EMAIL, self.html_content, re.IGNORECASE)
        unique_emails = list(dict.fromkeys(emails))
        self.results['emails'] = unique_emails
        return unique_emails
    
    def extract_phones(self) -> list:
        """
        Find phone numbers in the HTML content.
        
        Returns:
            list: List of unique phone numbers found
        """
        all_phones = []
        for pattern in RegexPatterns.PHONE_PATTERNS:
            phones = re.findall(pattern, self.html_content)
            all_phones.extend(phones)
        
        # Normalize and remove duplicates
        normalized_phones = []
        seen = set()
        for phone in all_phones:
            normalized = re.sub(r'[-.\s]', '', phone)
            if normalized not in seen:
                seen.add(normalized)
                normalized_phones.append(phone)
        
        self.results['phones'] = normalized_phones
        return normalized_phones
    
    def extract_urls(self) -> list:
        """
        Find all URLs in the web page.
        
        Includes:
        - Absolute URLs (http://, https://)
        - Relative URLs from href and src attributes
        
        Returns:
            list: List of unique URLs found
        """
        all_urls = []
        
        # Find absolute URLs
        absolute_urls = re.findall(RegexPatterns.URL, self.html_content)
        all_urls.extend(absolute_urls)
        
        # Find URLs from href attributes
        href_matches = re.findall(RegexPatterns.HREF, self.html_content, re.IGNORECASE)
        for href in href_matches:
            if href.startswith(('http://', 'https://')):
                all_urls.append(href)
            elif href.startswith('/'):
                # Convert relative URL to absolute
                all_urls.append(urljoin(self.base_url, href))
            elif not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                all_urls.append(urljoin(self.url, href))
        
        # Remove duplicates and clean up
        unique_urls = []
        seen = set()
        for url in all_urls:
            clean_url = url.split('#')[0].rstrip('/')
            if clean_url and clean_url not in seen:
                seen.add(clean_url)
                unique_urls.append(clean_url)
        
        self.results['urls'] = unique_urls
        return unique_urls
    
    def extract_ip_addresses(self) -> list:
        """
        Find IP addresses in the web page.
        
        Returns:
            list: List of IP addresses found
        """
        ips = re.findall(RegexPatterns.IP_ADDRESS, self.html_content)
        unique_ips = list(dict.fromkeys(ips))
        self.results['ip_addresses'] = unique_ips
        return unique_ips
    
    def extract_social_media(self) -> dict:
        """
        Find social media links in the web page.
        
        Supports: Facebook, Twitter/X, Instagram, LinkedIn, YouTube, TikTok, LINE
        
        Returns:
            dict: Dictionary of social media platforms and their links
        """
        social_links = {}
        for platform, pattern in RegexPatterns.SOCIAL_MEDIA.items():
            matches = re.findall(pattern, self.html_content, re.IGNORECASE)
            if matches:
                social_links[platform] = list(dict.fromkeys(matches))
        
        self.results['social_media'] = social_links
        return social_links
    
    def extract_page_info(self) -> tuple:
        """
        Extract basic info from the web page.
        
        Returns:
            tuple: (title, meta_description)
        """
        # Extract title
        title_match = re.search(RegexPatterns.TITLE, self.html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Title not found"
        
        # Extract meta description
        desc_match = re.search(RegexPatterns.META_DESC, self.html_content, re.IGNORECASE)
        if not desc_match:
            # Try an alternative format (content before name)
            alt_pattern = r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']'
            desc_match = re.search(alt_pattern, self.html_content, re.IGNORECASE)
        
        description = desc_match.group(1).strip() if desc_match else "Meta description not found"
        
        self.results['page_title'] = title
        self.results['meta_description'] = description
        return (title, description)
    
    def analyze(self) -> dict:
        """
        Run a complete analysis.
        
        Returns:
            dict: All analysis results
        """
        if not self.html_content:
            if not self.fetch_page():
                return {}
        
        print("\n📊 Analyzing web page with Regular Expressions...")
        print("=" * 60)
        
        # Extract page info
        title, description = self.extract_page_info()
        print(f"\n📄 Page Title: {title}")
        print(f"📝 Meta Description: {description[:100]}..." if len(description) > 100 else f"📝 Meta Description: {description}")
        
        # Extract various data
        emails = self.extract_emails()
        phones = self.extract_phones()
        urls = self.extract_urls()
        ips = self.extract_ip_addresses()
        social = self.extract_social_media()
        
        return self.results
    
    def get_statistics(self) -> dict:
        """
        Generate statistics from the extracted data.
        
        Returns:
            dict: Various statistics
        """
        # Analyze frequently found domains
        domains = []
        for url in self.results['urls']:
            try:
                domain = urlparse(url).netloc
                if domain:
                    domains.append(domain)
            except:
                pass
        
        domain_counter = Counter(domains)
        
        # Analyze email domains
        email_domains = [email.split('@')[1] for email in self.results['emails'] if '@' in email]
        email_domain_counter = Counter(email_domains)
        
        stats = {
            'total_emails': len(self.results['emails']),
            'total_phones': len(self.results['phones']),
            'total_urls': len(self.results['urls']),
            'total_ips': len(self.results['ip_addresses']),
            'total_social_platforms': len(self.results['social_media']),
            'top_domains': domain_counter.most_common(10),
            'email_domains': email_domain_counter.most_common(5),
            'internal_links': len([u for u in self.results['urls'] if self.base_url in u]),
            'external_links': len([u for u in self.results['urls'] if self.base_url not in u]),
        }
        
        return stats
    
    def print_results(self):
        """
        Display results in a formatted output.
        """
        print("\n" + "=" * 60)
        print("📊 Web Page Analysis Results")
        print("=" * 60)
        
        # Emails
        print(f"\n📧 Emails found ({len(self.results['emails'])} items):")
        print("-" * 40)
        if self.results['emails']:
            for i, email in enumerate(self.results['emails'][:20], 1):
                print(f"  {i}. {email}")
            if len(self.results['emails']) > 20:
                print(f"  ... and {len(self.results['emails']) - 20} more")
        else:
            print("  No emails found")
        
        # Phones
        print(f"\n📞 Phone numbers found ({len(self.results['phones'])} items):")
        print("-" * 40)
        if self.results['phones']:
            for i, phone in enumerate(self.results['phones'][:20], 1):
                print(f"  {i}. {phone}")
            if len(self.results['phones']) > 20:
                print(f"  ... and {len(self.results['phones']) - 20} more")
        else:
            print("  No phone numbers found")
        
        # URLs
        print(f"\n🔗 URLs found ({len(self.results['urls'])} items):")
        print("-" * 40)
        if self.results['urls']:
            for i, url in enumerate(self.results['urls'][:15], 1):
                display_url = url[:70] + "..." if len(url) > 70 else url
                print(f"  {i}. {display_url}")
            if len(self.results['urls']) > 15:
                print(f"  ... and {len(self.results['urls']) - 15} more")
        else:
            print("  No URLs found")
        
        # IP Addresses
        if self.results['ip_addresses']:
            print(f"\n🌐 IP Addresses found ({len(self.results['ip_addresses'])} items):")
            print("-" * 40)
            for i, ip in enumerate(self.results['ip_addresses'][:10], 1):
                print(f"  {i}. {ip}")
        
        # Social Media
        if self.results['social_media']:
            print(f"\n📱 Social Media found:")
            print("-" * 40)
            for platform, links in self.results['social_media'].items():
                print(f"  {platform.capitalize()}: {len(links)} links")
                for link in links[:3]:
                    print(f"    - {link}")
        
        # Statistics
        stats = self.get_statistics()
        print("\n" + "=" * 60)
        print("📈 Summary Statistics")
        print("=" * 60)
        print(f"  • Total Emails: {stats['total_emails']}")
        print(f"  • Total Phone Numbers: {stats['total_phones']}")
        print(f"  • Total URLs: {stats['total_urls']}")
        print(f"    - Internal Links: {stats['internal_links']}")
        print(f"    - External Links: {stats['external_links']}")
        print(f"  • Total IP Addresses: {stats['total_ips']}")
        print(f"  • Social Media Platforms: {stats['total_social_platforms']}")
        
        if stats['top_domains']:
            print(f"\n  🏆 Top 5 Most Frequent Domains:")
            for domain, count in stats['top_domains'][:5]:
                print(f"    - {domain}: {count} times")
    
    def export_to_csv(self, filename: str = None):
        """
        Export data to CSV files.
        
        Args:
            filename: File name (auto-generated if not specified)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(self.url).netloc.replace('.', '_')
            filename = f"web_analysis_{domain}_{timestamp}.csv"
        
        # Export emails
        if self.results['emails']:
            email_file = filename.replace('.csv', '_emails.csv')
            with open(email_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['No.', 'Email', 'Domain'])
                for i, email in enumerate(self.results['emails'], 1):
                    domain = email.split('@')[1] if '@' in email else ''
                    writer.writerow([i, email, domain])
            print(f"✅ Emails saved: {email_file}")
        
        # Export phones
        if self.results['phones']:
            phone_file = filename.replace('.csv', '_phones.csv')
            with open(phone_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['No.', 'Phone Number'])
                for i, phone in enumerate(self.results['phones'], 1):
                    writer.writerow([i, phone])
            print(f"✅ Phone numbers saved: {phone_file}")
        
        # Export URLs
        if self.results['urls']:
            url_file = filename.replace('.csv', '_urls.csv')
            with open(url_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['No.', 'URL', 'Domain', 'Type'])
                for i, url in enumerate(self.results['urls'], 1):
                    try:
                        domain = urlparse(url).netloc
                        link_type = 'Internal' if self.base_url in url else 'External'
                    except:
                        domain = ''
                        link_type = 'Unknown'
                    writer.writerow([i, url, domain, link_type])
            print(f"✅ URLs saved: {url_file}")
        
        # Export summary
        summary_file = filename.replace('.csv', '_summary.csv')
        stats = self.get_statistics()
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Analyzed URL', self.url])
            writer.writerow(['Page Title', self.results['page_title']])
            writer.writerow(['Analysis Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(['Total Emails', stats['total_emails']])
            writer.writerow(['Total Phone Numbers', stats['total_phones']])
            writer.writerow(['Total URLs', stats['total_urls']])
            writer.writerow(['Internal Links', stats['internal_links']])
            writer.writerow(['External Links', stats['external_links']])
            writer.writerow(['Total IP Addresses', stats['total_ips']])
        print(f"✅ Summary saved: {summary_file}")
        
        return filename


def main():
    """
    Main function to run the program.
    """
    print("\n" + "=" * 70)
    print("🌐 Single-Page Web Analyzer using Regular Expression")
    print("📚 Theory of Computation Project")
    print("=" * 70)
    
    while True:
        print("\n" + "-" * 50)
        print("Main Menu:")
        print("  1. Analyze a web page")
        print("  2. Exit")
        print("-" * 50)
        
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            url = input("\n🔗 Enter the URL to analyze: ").strip()
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Create analyzer and run analysis
            analyzer = WebAnalyzer(url)
            results = analyzer.analyze()
            
            if results:
                analyzer.print_results()
                
                # Ask if user wants to export
                export_choice = input("\n💾 Export results to CSV? (y/n): ").strip().lower()
                if export_choice == 'y':
                    analyzer.export_to_csv()
            
        elif choice == '2':
            print("\n👋 Thank you for using the analyzer! Goodbye!")
            break
            
        else:
            print("❌ Please select 1 or 2 only")


if __name__ == "__main__":
    main()
