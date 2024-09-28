import torch
import requests
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from settings import OPENAI_API_KEY

class APIClient:
    
    def __init__(self):
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    def analyze_emergency(self, image_base64):
        image = Image.open(image_base64)
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.clip_model.get_text_features(**inputs)
        
        clip_text_output = outputs[0].cpu().numpy().tolist()  
        
        prompt = (
            f"You are a First Responder Analyst. Based on the following description of an image: '{clip_text_output}', "
            "analyze the incident and suggest which first responders (police, firefighters, EMTs, paramedics) "
            "should be deployed. Also, determine the severity of the emergency, and provide a confidence percentage "
            "for your analysis. If the description does not indicate an emergency, respond with a message saying: "
            "'This does not appear to be an emergency or the wrong image has been provided. Please re-submit the image.'"
        )
        
        return self._send_to_gpt(prompt)
    
    def _send_to_gpt(self, prompt):
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4",
            "prompt": prompt,
            "max_tokens": 500
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200 and "choices" in response.json():
            return response.json()["choices"][0]["text"]
        else:
            return {"error": "Invalid response format"}
    
    def analyze_data(self, firellava_analysis, user_category, user_description):
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = f"Analyze this emergency situation: {firellava_analysis}, User Category: {user_category}, User Description: {user_description}."
        data = {
            "model": "gpt-4",
            "prompt": prompt,
            "max_tokens": 500
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 and "choices" in response.json():
            return response.json()["choices"][0]["text"]
        else:
            return {"error": "Invalid response format"}
