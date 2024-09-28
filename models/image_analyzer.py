import requests
from settings import OPENAI_API_KEY

class ImageAnalyzer:
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = "gpt-4"
    
    def analyze_image_for_crime_or_disaster(self, image_base64):
        objects_detected, caption = self.detect_objects_in_image(image_base64)
        severity = self.detect_severity(caption)
        illegal_activity = self.detect_illegal_activity(objects_detected)
        person_descriptions = None
        if "person" in objects_detected:
            person_descriptions = self.describe_people_in_image(image_base64)
        else:
            person_descriptions = ["No people detected in the image."]
        suspect_description = None
        if illegal_activity:
            suspect_description = self.describe_suspect(image_base64)
        
        return {
            "illegal_activity": illegal_activity,
            "suspect_description": suspect_description,
            "person_descriptions": person_descriptions,
            "caption": caption,
            "severity": severity
        }
    
    def detect_objects_in_image(self, image_base64):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What objects do you detect in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        data = {
            "model": "gpt-4-turbo",
            "messages": prompt,
            "max_tokens": 300
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        
        if "choices" in response_json and response_json["choices"]:
            gpt_response_content = response_json["choices"][0]["message"]["content"]
            objects_detected = self._parse_objects_from_caption(gpt_response_content)
            return objects_detected, gpt_response_content
        else:
            return ["No objects detected"], "No valid caption"
    
    def _parse_objects_from_caption(self, caption):
        objects = []
        if "person" in caption:
            objects.append("person")
        if "knife" in caption:
            objects.append("knife")
        if "gun" in caption:
            objects.append("gun")
        if "car" in caption:
            objects.append("car")
        if "fire" in caption:
            objects.append("fire")
        return objects
    
    def detect_illegal_activity(self, objects_detected):
        if "knife" in objects_detected or "gun" in objects_detected:
            return "Weapon detected, possible illegal activity"
        return None
    
    def describe_people_in_image(self, image_base64):
        prompt = f"Describe the people in the image and their actions."
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "prompt": prompt, "max_tokens": 200}
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["text"].strip().split("\n")
        return ["No people descriptions available"]
    
    def describe_suspect(self, image_base64):
        prompt = "Based on the image, describe the suspect, including appearance and behavior."
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "prompt": prompt, "max_tokens": 150}
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["text"].strip()
        return "Description unavailable"
    
    def detect_severity(self, caption):
        if "fire" in caption or "explosion" in caption or "destruction" in caption:
            return "high"
        return "low"
