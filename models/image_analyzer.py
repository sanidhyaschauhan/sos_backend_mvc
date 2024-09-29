import requests
import logging
import json
import re
from settings import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

class ImageAnalyzer:
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = "gpt-4-turbo"
    
    def analyze_image_for_crime_or_disaster(self, image_base64):
        image_analysis = self._analyze_image_with_gpt_vision(image_base64)
        
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
        objects_detected = self._parse_objects_from_caption(caption)  # Use the new method here
        severity = self.detect_severity(caption)  # Now, this will work
        illegal_activity = self.detect_illegal_activity(objects_detected)  # Now, this will work
        person_descriptions = None
        
        if "person" in objects_detected:
            # First describe the people
            person_descriptions = self.describe_people_in_image(image_base64)
            
            # Now, ask GPT if any crime is being committed
            crime_detected, suspect_description = self._check_for_crime(image_base64)
            
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

    def _analyze_image_with_gpt_vision(self, base64_image):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Format the prompt properly with base64 image data
        prompt = [
            {
                "role": "user",
                "content": f"What’s in this image? data:image/jpeg;base64,{base64_image}"
            }
        ]

        data = {
            "model": "gpt-4-turbo",
            "messages": prompt,
            "max_tokens": 300
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            
            if "choices" in response_json and response_json["choices"]:
                gpt_response_content = response_json["choices"][0]["message"]["content"]
                return {"image_description": gpt_response_content}  
            else:
                logging.error(f"Invalid response format from GPT-4 Vision API: {response.text}")
                return {"error": "Invalid response format from GPT-4 Vision API"}
        except requests.exceptions.RequestException as e:
            logging.error(f"RequestException while calling GPT-4 Vision API: {e}")
            return {"error": f"Failed to analyze image with GPT-4 Vision: {e}"}
        except ValueError:
            logging.error("Invalid JSON response from GPT-4 Vision API.")
            return {"error": "Invalid JSON response from GPT-4 Vision API"}
    
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
        
        response = self._send_to_gpt(prompt)
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
        
        response = self._send_to_gpt(prompt)
        if "error" in response:
            logging.error(f"Error describing people: {response['error']}")
            return ["Unable to describe people in the image."]
        
        return [response]
    
    def _send_to_gpt(self, prompt):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            # Log the raw response to understand what is being returned
            logging.info(f"Raw GPT-4 API Response: {response.text}")

            response_json = response.json()  # Try parsing the response as JSON

            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
            else:
                logging.error("Invalid response format from GPT-4 Vision API.")
                return {"error": "Invalid response format from GPT-4 Vision API"}
        except requests.exceptions.RequestException as e:
            logging.error(f"RequestException while calling GPT-4 Vision API: {e}")
            return {"error": f"Failed to get response from GPT-4 Vision API: {e}"}
        except ValueError as ve:
            # Handle non-JSON response
            logging.error(f"Invalid JSON response from GPT-4 Vision API: {ve}")
            logging.error(f"Raw Response: {response.text}")
            return {"error": f"Received a non-JSON response: {response.text}"}


    def _parse_objects_from_caption(self, caption):
        objects = []
        keywords = ["person", "knife", "gun", "car", "fire", "weapon", "crime", "incident"]
        if caption:
            for keyword in keywords:
                if keyword in caption.lower():
                    objects.append(keyword)
        return objects

    # New method to detect severity based on keywords in the caption
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
