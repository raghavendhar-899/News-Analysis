from analyze import get_summary
import scrape
import verify

# Defining main function 
def main(company,country):
    data = scrape.Scrape_links(company,country)
    data = verify.stockify(data,company)
    for i in range(len(data)):
        # data = verify.stockify(data,company)
        body_text = scrape.scrape_article(data[i][1])
        summary = get_summary(body_text)
        data[i].append(summary)
    return data
# print(main('apple','us'))
