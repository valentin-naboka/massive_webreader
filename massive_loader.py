from typing import List, Optional
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

address = "https://network.joinmassive.com:65535"

class MassiveWebReader(BaseReader):
    """Playwright web page reader.

    Reads pages by rendering them with Playwright.
    """

    def __init__(self, headless: bool = True, creds: Optional[dict] = None, params: Optional[dict] = None):
        """Initialize with parameters."""
        self._headless = headless
        self._proxy = creds
        self._proxy["username"]+="-" + "country" + "-" + params["country"]
        self._proxy["server"]=address

        print(self._proxy)

    def load_data(self, urls: List[str]) -> List[Document]:
        """Load data from the input urls.

        Args:
            urls (List[str]): List of URLs to scrape.

        Returns:
            List[Document]: List of documents.
        """
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
            
            # Create a context with a real user agent and other human-like properties
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="en-US",
                timezone_id="America/New_York",
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
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
                    page.wait_for_timeout(2000) 
                    
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
