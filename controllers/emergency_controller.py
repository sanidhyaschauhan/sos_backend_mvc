from flask import request, jsonify
from models.emergency_model import EmergencyModel

class EmergencyController:
    
    @staticmethod
    def analyze():
        data = request.json
        image_base64 = data.get('image_base64')
        user_id = data.get('user_id')
        user_category = data.get('category', '')
        user_description = data.get('description', '')
        location = data.get('location', '')
        
        emergency_model = EmergencyModel()
        result = emergency_model.process_emergency(image_base64, user_id, user_category, user_description, location)
        
        return jsonify(result)
