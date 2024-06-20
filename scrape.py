import requests
from bs4 import BeautifulSoup
import verify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# from serpapi import GoogleSearch

def scrape_article(link):
    """
    Scrapes a news article link and returns the title, body text, and numeric data.

    Args:
        link (str): The URL of the news article.

    Returns:
        dict: A dictionary containing the title, body text.
    """

    # Set up the Selenium WebDriver
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Load the webpage
    # url = 'https://example.com'
    driver.get(link)

    print('Driver done')

    # Wait for the JavaScript to execute and the page to fully load
    time.sleep(2)  # You can adjust the sleep time based on the page load time

    print("sleep done")

    # Get the page source after JavaScript execution
    page_source = driver.page_source

    print("page source done")

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    print("soup done")


    # Scrape the page
    # page = requests.get(link)
    # soup = BeautifulSoup(page.content, 'html.parser')

    # Extract the title
    # title = soup.find('h1').text.strip()

    # Extract the body text
    body_text = []
    for paragraph in soup.find_all('p'):
        body_text.append(paragraph.text.strip())
    body_text = ' '.join(body_text)

    # # Extract numeric data (requires specific logic based on the website structure)
    # numeric_data = []
    # # Example: Extract numbers from a specific class
    # for element in soup.find_all('span', class_='number'):
    #     numeric_data.append(float(element.text.strip()))

    # Return the scraped data

    # 'numeric_data': numeric_data,
    return body_text


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
    # print(links,'links')
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

    # print(links[0])
    
    # Print the total number of links
    print('Total links:', len(links))
    return links

# Test
# Scrape_links('Infosys','IN')
# Scrape_links('Infosys','US')
# print(scrape_article('https://timesofindia.indiatimes.com/business/india-business/infosys-wins-100-million-ikea-deal/articleshow/111007179.cms'))
