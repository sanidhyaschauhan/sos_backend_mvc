import requests
from requests.exceptions import RequestException
from settings import OPENAI_API_KEY, HUGGINGFACE_API_KEY
import logging
import json
import base64
import re

logging.basicConfig(level=logging.INFO)

class APIClient:

    def analyze_emergency(self, base64_image):
        try:
            # Step 1: Get the image caption from Hugging Face
            huggingface_response = self._analyze_image_with_huggingface(base64_image)

            if 'error' in huggingface_response:
                logging.error(f"Hugging Face API Error: {huggingface_response['error']}")
                return huggingface_response

            caption = huggingface_response[0].get('generated_text', None)
            if caption:
                logging.info(f"Received caption: {caption}")
            else:
                return {"error": "Invalid Hugging Face response: 'generated_text' key not found"}

            # Step 2: Pass the caption to OpenAI GPT with a prompt
            prompt = (
                f"You are a First Responder Analyst. Based on the following description of an image: '{caption}', "
                "analyze the incident and suggest which first responders (police, firefighters, EMTs, paramedics) "
                "should be deployed. Also, determine the severity of the emergency, and provide a confidence percentage "
                "for your analysis.\n\n"
                "Please provide your response in the following JSON format:\n"
                "{\n"
                '  "first_responders": ["list", "of", "responders"],\n'
                '  "severity": "low",\n'
                '  "confidence": 90\n'
                "}\n\n"
                "If the description does not indicate an emergency, respond with a message saying: "
                "'This does not appear to be an emergency or the wrong image has been provided. Please re-submit the image.'"
            )

            gpt_response = self._send_to_gpt(prompt)

            if 'error' in gpt_response:
                logging.error(f"OpenAI API Error: {gpt_response['error']}")
                return gpt_response

            # Step 3: Attempt to extract valid JSON from GPT response
            gpt_analysis = self._extract_json_from_gpt_response(gpt_response)
            if gpt_analysis:
                return gpt_analysis
            else:
                return {"error": "Failed to extract valid JSON from GPT response.", "response": gpt_response}

        except Exception as e:
            logging.exception("An unexpected error occurred in analyze_emergency.")
            return {"error": f"An unexpected error occurred: {e}"}

    def _analyze_image_with_huggingface(self, base64_image):
        url = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }
        
        # Decode the base64 image
        image_data = base64.b64decode(base64_image)

        try:
            response = requests.post(url, headers=headers, data=image_data)
            response.raise_for_status()
            response_json = response.json()
            return response_json  # This will contain the generated caption
        except RequestException as e:
            logging.error(f"RequestException while calling Hugging Face API: {e}")
            return {"error": f"Failed to analyze image with Hugging Face: {e}"}
        except ValueError:
            logging.error("Invalid JSON response from Hugging Face API.")
            return {"error": "Invalid JSON response from Hugging Face API"}

    def _send_to_gpt(self, prompt):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
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
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
            else:
                logging.error("Invalid response format from OpenAI API.")
                return {"error": "Invalid response format from OpenAI API"}
        except RequestException as e:
            logging.error(f"RequestException while calling OpenAI API: {e}")
            return {"error": f"Failed to get response from OpenAI API: {e}"}
        except ValueError:
            logging.error("Invalid JSON response from OpenAI API.")
            return {"error": "Invalid JSON response from OpenAI API"}

    def _extract_json_from_gpt_response(self, gpt_response):
        try:
            # Use a regular expression to find JSON-like content within the response
            json_match = re.search(r"\{.*?\}", gpt_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                logging.error("No valid JSON found in GPT response.")
                return None
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Failed to parse GPT response as JSON: {e}")
            return None

    def analyze_data(self, firellava_analysis, user_category, user_description):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = (
            f"Analyze this emergency situation: {firellava_analysis}, "
            f"User Category: {user_category}, User Description: {user_description}.\n\n"
            "Please provide your response in the following JSON format:\n"
            "{\n"
            '  "analysis": "your analysis here",\n'
            '  "recommendations": ["list", "of", "recommendations"]\n'
            "}"
        )
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                gpt_response = response_json["choices"][0]["message"]["content"]
                try:
                    analysis_result = self._extract_json_from_gpt_response(gpt_response)
                    return analysis_result
                except json.JSONDecodeError:
                    logging.error("Failed to parse GPT response as JSON.")
                    return {"error": "Failed to parse GPT response as JSON.", "response": gpt_response}
            else:
                logging.error("Invalid response format from OpenAI API.")
                return {"error": "Invalid response format from OpenAI API"}
        except RequestException as e:
            logging.error(f"RequestException while calling OpenAI API: {e}")
            return {"error": f"Failed to get response from OpenAI API: {e}"}
        except ValueError:
            logging.error("Invalid JSON response from OpenAI API.")
            return {"error": "Invalid JSON response from OpenAI API"}
