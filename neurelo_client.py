import requests
from settings import NEURELO_API_URL, NEURELO_API_KEY

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
