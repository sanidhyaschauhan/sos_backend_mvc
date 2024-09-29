from models.api_client import APIClient
from neurelo_client import NeureloClient
from models.image_analyzer import ImageAnalyzer
from settings import NEURELO_API_KEY, NEURELO_API_URL
import requests
import json

class EmergencyModel:
    
    def __init__(self):
        self.neurelo_client = NeureloClient()
        self.image_analyzer = ImageAnalyzer()
    
    def process_emergency(self, image_base64, user_id, user_category, user_description, location):
        api_client = APIClient()
        firellava_analysis = api_client.analyze_emergency(image_base64)
        llama_analysis = api_client.analyze_data(firellava_analysis, user_category, user_description)
        image_analysis = self.image_analyzer.analyze_image_for_crime_or_disaster(image_base64)
        severity = image_analysis.get('severity', 'low')
        is_real_report = self.determine_real_report(location, severity, image_analysis)

        result = {
            "image_analysis": json.dumps(firellava_analysis),
            "llama_analysis": json.dumps(llama_analysis),
            "severity": severity,
            "location": location,
            "is_real_report": is_real_report,
            "illegal_activity": image_analysis["illegal_activity"],
            "suspect_description": image_analysis["suspect_description"],
            "person_descriptions": image_analysis["person_descriptions"]
            #"updated_at": now,  # Add the correct timestamp
            #"created_at": now    # Add the correct timestamp
        }

        self.store_analysis_results_in_db(result)
        
        return result
    
    def determine_real_report(self, location, severity, image_analysis):
        crowd_reports = self.neurelo_client.get_reports_from_location(location)
        
        if len(crowd_reports) > 1:
            return True
        
        if severity == 'high' or image_analysis["illegal_activity"]:
            return True
        
        return False
    
    def store_analysis_results_in_db(self, data):
        headers = {
            "X-API-KEY": NEURELO_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(NEURELO_API_URL, headers=headers, json=data)
        if response.status_code == 200 or response.status_code == 201:
            print("Data successfully stored in Neurelo database.")
        else:
            print(f"Failed to store data in Neurelo database. Status code: {response.status_code}, Response: {response.text}")
