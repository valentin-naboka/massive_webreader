from typing import List, Optional
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import copy

MASSIVE_PROXY_ADDRESS = "https://network.joinmassive.com:65535"

# Configuration for browser localization based on country code
COUNTRY_CONFIG = {
    "US": {"locale": "en-US", "timezone": "America/New_York"},
    "DE": {"locale": "de-DE", "timezone": "Europe/Berlin"},
    "CA": {"locale": "en-CA", "timezone": "America/Toronto"},
    "IT": {"locale": "it-IT", "timezone": "Europe/Rome"},
    "ES": {"locale": "es-ES", "timezone": "Europe/Madrid"},
    "PL": {"locale": "pl-PL", "timezone": "Europe/Warsaw"},
    "CZ": {"locale": "cs-CZ", "timezone": "Europe/Prague"},
    "UA": {"locale": "uk-UA", "timezone": "Europe/Kiev"},
    # Default fallback
    "DEFAULT": {"locale": "en-US", "timezone": "UTC"},
}

class MassiveWebReader(BaseReader):
    """Massive web page reader.

    Reads pages by rendering them with Playwright using Massive proxy via configurable geolocation.
    """

    def __init__(self, headless: bool = True, creds: Optional[dict] = None, params: Optional[dict] = None):
        """Initialize with parameters.
        
        Args:
            headless (bool): Whether to run browser in headless mode.
            creds (dict): Proxy credentials {'username': '...', 'password': '...'}.
            params (dict): Extra params, e.g., {'country': 'DE'}.
        """
        self._headless = headless
        self._creds = creds or {}
        self._params = params or {}
        
        # Construct proxy configuration if credentials are provided
        self._proxy = None
        if self._creds:
            # Create a copy to avoid mutating the original dictionary
            username = self._creds.get("username", "")
            password = self._creds.get("password", "")
            
            # Append country to username if specified
            country = self._params.get("country")
            if country:
                username = f"{username}-country-{country}"
                
            self._proxy = {
                "server": MASSIVE_PROXY_ADDRESS,
                "username": username,
                "password": password
            }

    def load_data(self, urls: List[str]) -> List[Document]:
        """Load data from the input urls.

        Args:
            urls (List[str]): List of URLs to scrape.

        Returns:
            List[Document]: List of documents.
        """
        # Determine locale and timezone based on country param
        country = self._params.get("country", "DEFAULT")
        config = COUNTRY_CONFIG.get(country, COUNTRY_CONFIG["DEFAULT"])
        
        documents = []
        with sync_playwright() as p:
            # Launch with arguments to hide automation
            browser = p.chromium.launch(
                headless=self._headless,
                proxy=self._proxy,
                args=[
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            
            # Create a context with a real user agent and localized properties
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale=config["locale"],
                timezone_id=config["timezone"],
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": f"{config['locale']},en;q=0.9",
                    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"macOS"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                }
            )
            
            # Add init script to hide webdriver property
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = context.new_page()
            
            for url in urls:
                try:
                    print(f"Navigating to {url}...")
                    page.goto(url, wait_until="domcontentloaded")
                    # Wait a bit for dynamic content to settle
                    page.wait_for_timeout(5000) 
                    
                    content = page.content()
                    
                    # Clean up HTML with BeautifulSoup
                    soup = BeautifulSoup(content, "html.parser")
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                        
                    text = soup.get_text(separator="\n")
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    documents.append(Document(text=text, extra_info={"url": url}))
                    
                except Exception as e:
                    print(f"Error fetching {url}: {e}")
                
            browser.close()
            
        return documents
