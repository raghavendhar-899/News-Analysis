from analyze import get_summary,get_score
import scrape
import verify


# import concurrent.futures

# def process_article(data_element, company):
#     try:
#         print('Article scrape started')
#         body_text = scrape.scrape_article(data_element[1])
#         print('$$$$$$$Scraping done$$$$$$$$')
#         summary = get_summary(body_text)
#         print('*******Summary done******')
#         score = get_score(body_text, company)
#         print('---Score done---')
#         return data_element + [summary, score]
#     except Exception as e:
#         print(f"Error processing article {data_element[0]}: {e}")
#         return data_element + [None, None]  # Return None for summary and score if there's an error

# def main(company, country):
#     data = scrape.Scrape_links(company, country)
#     data = verify.stockify(data, company)
    
#     # Use ThreadPoolExecutor for I/O-bound tasks
#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         # Submit tasks to the executor
#         futures = [executor.submit(process_article, data[i], company) for i in range(len(data))]
        
#         # Retrieve results as they complete
#         for i, future in enumerate(concurrent.futures.as_completed(futures)):
#             data[i] = future.result()
    
#     return data


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
