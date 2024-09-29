import logging
from models.api_client import APIClient  

logging.basicConfig(level=logging.INFO)

class ImageAnalyzer:
    
    def __init__(self):
        self.client = APIClient()  # Use the existing APIClient
        self.delay = 1 

    def analyze_image_for_crime_or_disaster(self, base64_image):
        # Use the APIClient to get the analysis result
        image_analysis = self.client.analyze_emergency(base64_image)
        
        if 'error' in image_analysis:
            logging.error(f"Image analysis failed: {image_analysis['error']}")
            return {
                "illegal_activity": None,
                "image_analysis": image_analysis,
                "is_real_report": False,
                "llama_analysis": None,
                "location": None,
                "person_descriptions": ["No people detected in the image."],
                "severity": "low",
                "suspect_description": None
            }
        
        caption = image_analysis.get('image_description', None)
        objects_detected = self._parse_objects_from_caption(caption)  
        severity = self.detect_severity(caption)  
        illegal_activity = self.detect_illegal_activity(objects_detected)  
        person_descriptions = None
        
        if "person" in objects_detected:
            # First describe the people
            person_descriptions = self.describe_people_in_image(base64_image)
            
            # Now, ask GPT if any crime is being committed
            crime_detected, suspect_description = self._check_for_crime(base64_image)
            
            if crime_detected:
                return {
                    "illegal_activity": True,
                    "image_analysis": image_analysis,
                    "is_real_report": True,
                    "llama_analysis": None,
                    "location": None,
                    "person_descriptions": person_descriptions,
                    "severity": severity,
                    "suspect_description": suspect_description
                }
            else:
                return {
                    "illegal_activity": False,
                    "image_analysis": image_analysis,
                    "is_real_report": True,
                    "llama_analysis": None,
                    "location": None,
                    "person_descriptions": person_descriptions,
                    "severity": severity,
                    "suspect_description": None
                }
        else:
            return {
                "illegal_activity": None,
                "image_analysis": image_analysis,
                "is_real_report": True,
                "llama_analysis": None,
                "location": None,
                "person_descriptions": ["No people detected in the image."],
                "severity": severity,
                "suspect_description": None
            }

    def _check_for_crime(self, base64_image):
        prompt = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Is there anyone committing a crime in this image? If so, describe them."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        response = self.client._send_to_gpt(prompt)
        if "error" in response:
            logging.error(f"Error detecting crime: {response['error']}")
            return False, None

        if "no crime" in response.lower():
            return False, None
        else:
            # Crime detected, return suspect details
            return True, response
    
    def describe_people_in_image(self, base64_image):
        prompt = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe every person in this image in detail."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        response = self.client._send_to_gpt(prompt)
        if "error" in response:
            logging.error(f"Error describing people: {response['error']}")
            return ["Unable to describe people in the image."]
        
        return [response]

    def _parse_objects_from_caption(self, caption):
        objects = []
        keywords = ["person", "knife", "gun", "car", "fire", "weapon", "crime", "incident"]
        if caption:
            for keyword in keywords:
                if keyword in caption.lower():
                    objects.append(keyword)
        return objects

    # Method to detect severity based on keywords in the caption
    def detect_severity(self, caption):
        if not caption:
            return "low"
        
        high_severity_keywords = ["fire", "explosion", "gun", "knife", "weapon", "danger", "emergency", "crime"]
        medium_severity_keywords = ["accident", "injury", "fight", "incident", "disturbance", "problem"]

        caption_lower = caption.lower()

        # Check for high severity keywords
        for word in high_severity_keywords:
            if word in caption_lower:
                return "high"

        for word in medium_severity_keywords:
            if word in caption_lower:
                return "medium"

        return "low"

    def detect_illegal_activity(self, objects_detected):
        illegal_objects = ["knife", "gun", "weapon", "crime", "incident"]
        for obj in objects_detected:
            if obj in illegal_objects:
                return True
        return False
