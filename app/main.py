from app.services.analyze import get_summary, get_score
from app.services import scrape
from app.services import verify
from app.repository.company import Company
from app.repository.article import Article
from app.services.duckduckgo_API import get_company_news
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Defining main function 
def process_company_articles(company,country,isnew=False):
    # data = scrape.Scrape_links(company,country)
    data = get_company_news(company=company,country=country)
    # Article dict keys returned by get_company_news():
    # - date (str)
    # - title (str)
    # - body (str)
    # - url (str)
    # - image (str)
    # - source (str)
    # - search_query (str)   # added by us
    # - time_filter (str)    # added by us, "d" or "w"
    # - date_dt (datetime)   # added by us, e.g. datetime.datetime(2026, 3, 29, 11, 32, 45)
    # print(data)
    data_to_be_processed=[]
    articleobj = Article(company)
    for i in data:
        logger.info(i["title"])
        if not articleobj.find_article(i["title"]): # if article is not already present in the database
            data_to_be_processed.append(i)
    data = verify.stockify(data_to_be_processed,company,isnew)
    for i in range(len(data)):
        logger.info('article %s', i)
        body_text = scrape.scrape_article(data[i]["url"])
        logger.info('scraping done %s', data[i]["url"])
        summary = "Unable to summarize..."
        score = '--'
        logger.debug('body_text: %s', body_text)
        if body_text:
            summary = get_summary(body_text)
            logger.info('summary done')
            score = get_score(data[i]["title"],body_text,company,isnew)
            logger.info('score done')
        data[i]["summary"] = summary
        data[i]["score"] = score
    return data

def start():
    companyobj = Company()
    logger.info('init')
    while True:
        companies = companyobj.get_all_company_names()
        companies=companies[::-1]
        logger.info('all companies retrived ***************')
        for data in companies:
            get_article_data(data[0],data[1])
            score = calculate_score(data[0])
            logger.info('Score = --------- %s', score)
            companyobj.update_company_score(data[0],score)

# def new_company(name,location):
#     get_article_data(name,location,True)
#     companyobj = Company()
#     score = calculate_score(name)
#     print('Score = ---------',score)
#     companyobj.update_company_score(name,score)
        
def calculate_score(company):
    articleobj = Article(company)
    scores = articleobj.get_all_article_scores()
    valid_count = 0
    totalscore = 0
    for i in scores:
        if i!='--':
            valid_count+=1
            totalscore+=i
    if valid_count>0:
        return totalscore/valid_count
    return 0


def get_article_data(company,location,isnew=False):
    article_data = process_company_articles(company,location,isnew)
    articleobj = Article(company)
    for i in article_data:
        articleobj.insert_article(i["title"], i["url"], i["date_dt"], i["summary"], i["score"])

if __name__ == '__main__':
    start()
