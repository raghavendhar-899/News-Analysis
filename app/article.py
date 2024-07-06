from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
from database import get_database

class article:
    def __init__(self, collection_name):
        self.db = get_database()
        self.news_collection = self.db[collection_name]
        self.news_collection.create_index([('date', ASCENDING)], expireAfterSeconds=345600)

    def insert_article(self, title, link, date, summary, score):
        article = {
            "title": title,
            "link": link,
            "date": date,
            "summary": summary,
            "score": score
        }
        return self.news_collection.insert_one(article)

    def find_article(self, title):
        return self.news_collection.find_one({"title": title})

    def delete_article(self, title):
        return self.news_collection.delete_one({"title": title})

    def get_all_article(self):
        sort=list({'date': -1}.items())
        # return list(self.news_collection.find({}, sort=sort))
        return list(self.news_collection.find({}, {"_id": 0},sort=sort))
    
    def get_all_article_scores(self):
        articles = self.news_collection.find({}, {"_id": 0, "score": 1})
        return [article["score"] for article in articles]