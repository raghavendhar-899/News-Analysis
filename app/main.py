from analyze import get_summary,get_score
import scrape
import verify
from company import company
from article import article
import time

# Defining main function 
def main(company,country,isnew=False):
    data = scrape.Scrape_links(company,country)
    data_to_be_processed=[]
    articleobj = article(company)
    for i in data:
        print(i[0])
        if not articleobj.find_article(i[0]):
            data_to_be_processed.append(i)
    data = verify.stockify(data_to_be_processed,company,isnew)
    for i in range(len(data)):

        print('artical',i)
        body_text = scrape.scrape_article(data[i][1])
        print('scrapeing done')
        summary = "Unable to summarize..."
        score = '--'
        if body_text:
            summary = get_summary(body_text)
            print('summary done')
            score = get_score(body_text,company,isnew)
            print('score done \n')
        data[i].append(summary)
        data[i].append(score)
    return data

def start():
    companyobj = company()
    print('init')
    while True:
        companies = companyobj.get_all_company_names()
        print('all companies retrived ***************')
        for data in companies:
            if not get_article_data(data[0],data[1]):
                time.sleep(40)
                continue
            score = calculate_score(data[0])
            print('Score = ---------',score)
            companyobj.update_company_score(data[0],score)

def new_company(name,location):
    get_article_data(name,location,True)
    companyobj = company()
    score = calculate_score(name)
    print('Score = ---------',score)
    companyobj.update_company_score(name,score)
        
def calculate_score(company):
    articleobj = article(company)
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
    article_data = main(company,location,isnew)
    articleobj = article(company)
    for i in article_data:
        articleobj.insert_article(i[0],i[1],i[2],i[3],i[4])
    if len(article_data)<3:
        return False
    return True
