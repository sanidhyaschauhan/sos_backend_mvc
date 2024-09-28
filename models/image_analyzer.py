import requests
from settings import OPENAI_API_KEY

class ImageAnalyzer:
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = "gpt-4"
    
    def analyze_image_for_crime(self, image_base64):
        objects_detected = self.detect_objects_in_image(image_base64)
        illegal_activity = self.detect_illegal_activity(objects_detected)
        person_descriptions = self.describe_people_in_image(image_base64)
        suspect_description = None
        if illegal_activity:
            suspect_description = self.describe_suspect(objects_detected)
        return {
            "illegal_activity": illegal_activity,
            "suspect_description": suspect_description,
            "person_descriptions": person_descriptions
        }
    
    def detect_objects_in_image(self, image_base64):
        objects = ["person", "knife", "car"]
        return objects
    
    def detect_illegal_activity(self, objects_detected):
        if "knife" in objects_detected or "gun" in objects_detected:
            return "Weapon detected, possible illegal activity"
        return None
    
    def describe_people_in_image(self, image_base64):
        people_detected = ["person_1", "person_2", "person_3"]
        descriptions = []
        for person in people_detected:
            description = self.generate_description_for_person(person)
            descriptions.append(description)
        return descriptions
    
    def generate_description_for_person(self, person):
        prompt = f"Describe the appearance and actions of {person} based on the image."
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "prompt": prompt, "max_tokens": 100}
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        return f"Description for {person}"
    
    def describe_suspect(self, objects_detected):
        return "The suspect is a person holding a knife, wearing a black hoodie."
