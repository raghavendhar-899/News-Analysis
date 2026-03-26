import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebDriverSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebDriverSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialize_webdriver()
        return cls._instance

    def initialize_webdriver(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-infobars')
        prefs = {
    "profile.managed_default_content_settings.javascript": 1,
    "profile.default_content_settings.cookies": 1,
    "profile.block_third_party_cookies": False
        }
        self.options.add_experimental_option("prefs", prefs)
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.set_page_load_timeout(5)

    def get_driver(self):
        return self.driver

    def quit_driver(self):
        if self.driver:
            self.driver.quit()

# Instantiate the WebDriverSingleton
webdriver_singleton = WebDriverSingleton()
logger.info('web driver created')





def scrape_article(link):
    """
    Scrapes a news article link and returns the title, body text, and numeric data.

    Args:
        link (str): The URL of the news article.

    Returns:
        dict: A dictionary containing the title, body text.
    """

    driver = webdriver_singleton.get_driver()

    try:
        driver.get(link)
        logger.debug('driver.get completed for %s', link)

        # Wait for the JavaScript to execute and the page to fully load
        time.sleep(5)  # You can adjust the sleep time based on the page load time

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        logger.debug('page_source length=%d', len(page_source) if page_source else 0)

    except Exception as e:
        logger.error("Timed out waiting for page to load: %s", e)
        return None

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    logger.debug('parsed soup')


    # Extract the body text
    body_text = []
    for paragraph in soup.find_all('p'):
        logger.debug('paragraph len=%d', len(paragraph.text.strip()))
        body_text.append(paragraph.text.strip())
    body_text = ' '.join(body_text)

    return body_text


#Test
# Link='https://www.defenseworld.net/2024/05/28/infosys-limited-nyseinfy-shares-acquired-by-eversource-wealth-advisors-llc.html'
# print(scrape_article(Link))

def Scrape_links(stock,location='US'):
    # Create a list to store the links
    links = []

    base_url='https://news.google.com'
    logger.info('scraping links for %s (%s)', stock, location)
    url = base_url+'/search?q=' + stock +'%20when%3A1d'+ '&gl='+location
    response = requests.get(url)

    # Parse the webpage content with Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the link and heading
    all_links = soup.find_all('a', class_='JtKRv')

    for link in all_links:
        heading = link.get_text()
        href = base_url + link['href'][1:]

        # Find the datetime element that follows the current link element
        datetime_element = link.find_next('time', class_='hvbAAd')
        if datetime_element:
            datetime_str = datetime_element['datetime']
            date_time_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
        else:
            logger.debug('No datetime element found for link: %s', href)
            date_time_obj = None

        links.append([heading, href, date_time_obj])

    
    # Print the total number of links
    logger.info('Total links: %d', len(links))
    return links


# ------------------ Google News API ------------------
# def Scrape_links(stock: str, location: str = 'US'):
#     """
#     Fetches news articles using Google News API.
    
#     Args:
#         stock (str): The stock symbol or company name to search for
#         location (str): The country code for news location (default: 'US')
        
#     Returns:
#         List containing [title, url, datetime]
#     """
#     # Get API credentials from .env file
#     api_key = os.getenv('GOOGLE_API_KEY')
#     cx = os.getenv('GOOGLE_CX')
    
#     if not api_key or not cx:
#         raise ValueError("Google API credentials not found in .env file. Please ensure GOOGLE_API_KEY and GOOGLE_CX are set.")
    
#     base_url = "https://www.googleapis.com/customsearch/v1"
    
#     # Construct the query
#     query = f"{stock} News when:1d"
    
#     params = {
#         'key': api_key,
#         'cx': cx,
#         'q': query,
#         'gl': location,
#         'num': 10,  # Number of results to return
#         'sort': 'date'  # Sort by date
#     }
    
#     try:
#         response = requests.get(base_url, params=params)
#         response.raise_for_status()
#         data = response.json()
        
#         links = []
#         for item in data.get('items', []):
#             title = item.get('title', '')
#             url = item.get('link', '')
            
#             # Get the date from the snippet or use current time if not available
#             date_str = item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time')
#             if date_str:
#                 try:
#                     # Try parsing as ISO format first
#                     date_time_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
#                 except ValueError:
#                     try:
#                         # Try parsing as Unix timestamp
#                         date_time_obj = datetime.fromtimestamp(int(date_str))
#                     except (ValueError, TypeError):
#                         date_time_obj = None
#             else:
#                 date_time_obj = None
                
#             links.append([title, url, date_time_obj])
            
#         print('Total links:', len(links))
#         return links
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching news: {e}")
#         return []
# Test
# Scrape_links('Infosys','IN')
# Scrape_links('Infosys','US')
if __name__ == '__main__':
    test_link = 'https://news.google.com/read/CBMi2AFBVV95cUxNbHU4N25qbjRncTAzZlFma2NQUFBfYmpuVnVrSEdudjBReGNRNlctRUJFLWRnZU9qMWY2NWFoSTZUaW1mSERYRWV4RWwyYTRiRnEtSDFEcFEtdGI1RE1XcDRFOEthYUNlUVJfaExXUkYtWTJrTmJ0THMtY2NrV1JneTQ2M1p2WjAzUmJ6RnhqZWFDOGI2RHBkc0NCaVRXcUxTVEdyZVhPcmEzUTFrRTl1aFZEdG5OUzJ3cUdGaDlhVFQweEt2aDl6ZkVZdUw0M2x4aFR5MEE5c2w?hl=en-AU&gl=AU&ceid=AU%3Aen'
    logger.info('running scrape_article test')
    logger.info(scrape_article(test_link))
