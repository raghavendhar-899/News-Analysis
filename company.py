from pymongo import MongoClient
from database import get_database

class company:
    def __init__(self):
        self.db = get_database()
        self.companies_collection = self.db.companies

    def insert_company(self, name, locations, score, primary_location):
        company = {
            "name": name,
            "primary_location": primary_location,
            "locations": locations,
            "score": score
        }
        return self.companies_collection.insert_one(company)

    def find_company(self, name):
        return self.companies_collection.find_one({"name": name})

    def update_company_score(self, name, new_score):
        return self.companies_collection.update_one({"name": name}, {"$set": {"score": new_score}})

    def add_company_location(self, name, new_location):
        return self.companies_collection.update_one({"name": name}, {"$push": {"locations": new_location}})

    def get_all_company_names(self):
        companies = self.companies_collection.find({}, {"name": 1, "primary_location": 1})
        return [(company["name"], company["primary_location"]) for company in companies]
    
    def get_company_name_suggestions(self, query):
        regex_query = {"name": {"$regex": f'^{query}', "$options": 'i'}}
        suggestions = self.companies_collection.find(regex_query, {"name": 1}).limit(10)
        return [company["name"] for company in suggestions]