from analyze import get_summary
import scrape

# Defining main function 
def main(company,country):
    data = scrape.Scrape_links(company,country)
    for i in range(len(data)):
        if i==3:
            break
        body_text = scrape.scrape_article(data[i][1])
        summary = get_summary(body_text)
        data[i].append(summary)
    return data
print(main('apple','us'))
