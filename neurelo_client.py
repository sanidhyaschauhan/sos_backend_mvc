import requests
from settings import NEURELO_API_URL, NEURELO_API_KEY, NEURELO_API_URL_GET

class NeureloClient:
    
    def __init__(self):
        self.api_url = NEURELO_API_URL
        self.api_key = NEURELO_API_KEY
    
    def get_reports_from_location(self, location):
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        query_url = f"{self.api_url}/reports/location"
        response = requests.get(query_url, headers=headers, params={"location": location})
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_all_reports(self):
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        query_url = NEURELO_API_URL_GET
        response = requests.get(query_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

def store_analysis_results_in_db(data):
    headers = {
        "X-API-KEY": NEURELO_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(NEURELO_API_URL, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        print("Data successfully stored in Neurelo database.")
    else:
        print(f"Failed to store data in Neurelo database. Status code: {response.status_code}, Response: {response.text}")
