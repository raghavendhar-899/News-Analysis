import requests
from bs4 import BeautifulSoup
import verify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


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

        print('Driver done')

        # Wait for the JavaScript to execute and the page to fully load
        time.sleep(2)  # You can adjust the sleep time based on the page load time

        # Get the page source after JavaScript execution
        page_source = driver.page_source
    
    except:
        print("Timed out waiting for page to load")
        return None

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')


    # Extract the body text
    body_text = []
    for paragraph in soup.find_all('p'):
        body_text.append(paragraph.text.strip())
    body_text = ' '.join(body_text)

    return body_text

# Instantiate the WebDriverSingleton
webdriver_singleton = WebDriverSingleton()

#Test
# Link='https://www.defenseworld.net/2024/05/28/infosys-limited-nyseinfy-shares-acquired-by-eversource-wealth-advisors-llc.html'
# print(scrape_article(Link))

def Scrape_links(stock,location='US'):
    # Create a list to store the links
    links = []

    base_url='https://news.google.com'
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
            datetime = datetime_element['datetime']
        else:
            print('No datetime element found')
            datetime = None

        links.append([heading, href, datetime])

    
    # Print the total number of links
    print('Total links:', len(links))
    return links

# Test
# Scrape_links('Infosys','IN')
# Scrape_links('Infosys','US')
# print(scrape_article('https://timesofindia.indiatimes.com/business/india-business/infosys-wins-100-million-ikea-deal/articleshow/111007179.cms'))
