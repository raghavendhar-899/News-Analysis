from analyze import get_summary,get_score
import scrape
import verify
from company import company
from article import article

# Defining main function 
def main(company,country):
    data = scrape.Scrape_links(company,country)
    data = verify.stockify(data,company)
    for i in range(len(data)):
        print('artical',i)
        body_text = scrape.scrape_article(data[i][1])
        print('scrapeing done')
        summary = "Unable to summarize..."
        score = '--'
        if body_text:
            summary = get_summary(body_text)
            print('summary done')
            score = get_score(body_text,company)
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
            get_article_data(data[0],data[1])


def get_article_data(company,location):
    article_data = main(company,location)
    articleobj = article(company)
    for i in article_data:
        articleobj.insert_article(i[0],i[1],i[2],i[3],i[4])
