from flask import Flask, request, jsonify
from flask_cors import CORS
from models.emergency_model import EmergencyModel
from neurelo_client import NeureloClient

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/analyze', methods=['POST'])
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

@app.route('/getalldata', methods=['GET'])
def get_all_reports():
    try:
        neurelo_client = NeureloClient()
        all_reports = neurelo_client.get_all_reports()
        return jsonify(all_reports)
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

@app.route('/server_status', methods=['GET'])
def server_status():
    return "Server is up"


if __name__ == '__main__':
    app.run(debug=True)
