import requests
from settings import OPENAI_API_KEY

class APIClient:
    
    def analyze_emergency(self, image_base64):
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            "You are a First Responder Analyst and your job is to view the image and analyze "
            "what kind of incident has happened. Also classify which of the first responders "
            "(police, firefighters, emergency medical technicians-EMTs, and paramedics) should "
            "be deployed based on the image. You need to make sure that the image is actually of "
            "an emergency, consider this image as part of a 911 call. So, analyze and classify if "
            "the image is of an emergency and also assign severity of the emergency. If the image "
            "doesn't seem like an emergency, you need to return a message saying - 'From the image, "
            "this emergency isn't clear or wrong image has been attached. Please call us or re-submit "
            "the photo'. Also give the confidence of your analysis in NUMERIC percentage always."
        )
        
        data = {
            "model": "gpt-4o",
            "prompt": prompt,
            "image": image_base64,
            "max_tokens": 500
        }
        
        response = requests.post(url, json=data, headers=headers)
        print(response.json())
        
        if "choices" in response.json():
            return response.json()["choices"][0]["text"]
        else:
            print("Error: 'choices' not found in the response.")
            return {"error": "Invalid response format"}
    
    def analyze_data(self, firellava_analysis, user_category, user_description):
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = f"Analyze this emergency situation: {firellava_analysis}, User Category: {user_category}, User Description: {user_description}."
        data = {
            "model": "gpt-4o",
            "prompt": prompt,
            "max_tokens": 500
        }
        response = requests.post(url, json=data, headers=headers)
        print(response.json())

        if "choices" in response.json():
            return response.json()["choices"][0]["text"]
        else:
            print("Error: 'choices' not found in the response.")
            return {"error": "Invalid response format"}
