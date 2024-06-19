from analyze import get_summary,get_score
import scrape
import verify

# Defining main function 
def main(company,country):
    data = scrape.Scrape_links(company,country)
    data = verify.stockify(data,company)
    for i in range(len(data)):
        # data = verify.stockify(data,company)
        print('artical',i)
        body_text = scrape.scrape_article(data[i][1])
        print('scrapeing done')
        summary = get_summary(body_text)
        print('summary done')
        score = get_score(body_text,company)
        print('score done')
        data[i].append(summary)
        data[i].append(score)
    return data
# print(main('apple','us'))
