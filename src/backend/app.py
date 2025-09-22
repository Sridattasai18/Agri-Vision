# AgriVision Backend
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from src.backend.chatbot.gemini_chatbot import integrate_chatbot_with_flask
from src.backend.utils.weather_api import get_weather_data, get_weather_forecast, WeatherAPIWrapper

# Create Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Use a secure default for production, but allow override for development
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key and os.environ.get('FLASK_DEBUG') == '1':
    app.secret_key = 'dev-secret-key' # A predictable key for development

CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------
# Load trained models
# ----------------------------
# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
DB_PATH = os.path.join(project_root, 'data', 'feedback.db')

# Crop recommendation model
model_path = os.path.join(project_root, 'models', 'crop_model (1).joblib')
crop_model = joblib.load(model_path)

# Load features
features_path = os.path.join(project_root, 'models', 'features (1).json')
with open(features_path, 'r') as f:
    features = json.load(f)

# Fertilizer CSV
fertilizer_path = os.path.join(project_root, 'data', 'fertilizer (2).csv')
fertilizer_df = pd.read_csv(fertilizer_path)

# ----------------------------
# Helper functions
# ----------------------------
def init_db():
    """Initialize the SQLite database for feedback."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def recommend_fertilizer(crop, N, P, K):
    """Recommend fertilizer based on crop and current NPK levels"""
    row = fertilizer_df[fertilizer_df['Crop'] == crop]
    if row.empty:
        return {"error": "Crop not found in fertilizer database"}
    
    # Get recommended NPK values for the crop
    rec_N = row['N'].values[0]
    rec_P = row['P'].values[0] 
    rec_K = row['K'].values[0]
    
    # Calculate deficiencies
    n_def = max(0, float(rec_N) - float(N))
    p_def = max(0, float(rec_P) - float(P))
    k_def = max(0, float(rec_K) - float(K))
    
    # Determine which nutrient is most deficient
    max_def = max(n_def, p_def, k_def)
    
    if max_def == 0:
        return {"message": "Soil nutrients are adequate for this crop", "type": "balanced"}
    elif max_def == n_def:
        return {
            "type": "Nitrogen",
            "deficiency": round(n_def, 2),
            "recommendation": f"Add {round(n_def, 2)} units of Nitrogen fertilizer",
            "fertilizer_type": "Urea or Ammonium Nitrate"
        }
    elif max_def == p_def:
        return {
            "type": "Phosphorus", 
            "deficiency": round(p_def, 2),
            "recommendation": f"Add {round(p_def, 2)} units of Phosphorus fertilizer",
            "fertilizer_type": "DAP or Superphosphate"
        }
    else:
        return {
            "type": "Potassium",
            "deficiency": round(k_def, 2), 
            "recommendation": f"Add {round(k_def, 2)} units of Potassium fertilizer",
            "fertilizer_type": "Potash or MOP"
        }

# ----------------------------
# Routes
# ----------------------------

@app.route('/')
def home():
    # Check if user is logged in
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': True,
        'features_count': len(features),
        'crop_classes': len(crop_model.classes_)
    })

@app.route('/api/predict/crop', methods=['POST'])
def predict_crop():
    try:
        data = request.get_json()
        required_features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for feature in required_features:
            if feature not in data:
                return jsonify({'success': False, 'error': f'Missing feature: {feature}'}), 400
        
        # Prepare input for model
        input_data = [[
            data['N'], data['P'], data['K'],
            data['temperature'], data['humidity'],
            data['ph'], data['rainfall']
        ]]
        
        # Predict crops
        predictions = crop_model.predict_proba(input_data)[0]
        crop_classes = crop_model.classes_
        top_predictions = sorted(
            [{'crop': crop_classes[i], 'probability': predictions[i]} for i in range(len(crop_classes))],
            key=lambda x: x['probability'], reverse=True
        )[:3]
        
        return jsonify({'success': True, 'predictions': top_predictions})
    except Exception as e:
        app.logger.error(f"Error in /api/predict/crop: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred while predicting the crop.'}), 500

@app.route('/api/predict/fertilizer', methods=['POST'])
def predict_fertilizer():
    try:
        data = request.json
        crop = data['crop']
        N = data['N']
        P = data['P']
        K = data['K']
        
        recommendation = recommend_fertilizer(crop, N, P, K)
        return jsonify({'success': True, 'data': recommendation})
    except Exception as e:
        app.logger.error(f"Error in /api/predict/fertilizer: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred while recommending fertilizer.'}), 500

@app.route('/api/weather', methods=['POST'])
def get_weather():
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        if not city:
            return jsonify({'success': False, 'error': 'City name is required'}), 400
        
        weather_data = get_weather_data(city)
        if not weather_data:
            return jsonify({'success': False, 'error': 'Failed to fetch weather data. Please check the city name or try again later.'}), 400
        
        return jsonify({'success': True, 'data': weather_data})
    except Exception as e:
        app.logger.error(f"Error in /api/weather: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred while fetching weather data.'}), 500

@app.route('/api/weather/forecast', methods=['POST'])
def weather_forecast():
    try:
        data = request.json
        city = data.get('city', '')
        if not city:
            return jsonify({'success': False, 'error': 'City name is required'}), 400
        forecast = get_weather_forecast(city)
        if 'error' in forecast:
            return jsonify({'success': False, 'error': forecast['error']}), 400
        return jsonify({'success': True, 'data': forecast})
    except Exception as e:
        app.logger.error(f"Error in /api/weather/forecast: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred while fetching the forecast.'}), 500

@app.route('/api/predict/disease', methods=['POST'])
def predict_disease():
    return jsonify({
        'success': True,
        'message': 'Plant Disease Detection feature is coming soon!',
        'status': 'under_development'
    })

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirmPassword = data.get('confirmPassword', '')
        firstName = data.get('firstName', '').strip()
        lastName = data.get('lastName', '').strip()
        role = data.get('role', '')
        termsAccepted = data.get('termsAccepted', False)
        
        # --- Input Validation ---
        # Validation
        if not all([username, email, password, firstName, lastName, role]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        if password != confirmPassword:
            return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
        
        if len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
        
        if not termsAccepted:
            return jsonify({'success': False, 'error': 'Please accept the terms and conditions'}), 400
        
        # --- Database Interaction ---
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        
        # Hash the password for security
        password_hash = generate_password_hash(password)
        
        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, firstName, lastName) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, password_hash, role, firstName, lastName)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': username
        })
        
    except Exception as e:
        app.logger.error(f"Error in /api/signup: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred during signup.'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        role = data.get('role', '')
        
        # --- Database Interaction ---
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        # --- Authentication Logic ---
        if user and check_password_hash(user['password_hash'], password):
            # User exists and password hash matches, now check role
            if user['role'] == role:
                session['user'] = username
                session['role'] = user['role']
                return jsonify({
                    'success': True,
                    'user': username,
                    'role': user['role'],
                    'message': 'Login successful'
                })
            else:
                # Correct user/pass but wrong role
                return jsonify({'success': False, 'error': 'The selected role does not match this user.'}), 401
        else:
            # Incorrect username or password
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
    except Exception as e:
        app.logger.error(f"Error in /api/login: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred during login.'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user' in session:
        return jsonify({
            'success': True,
            'user': session['user'],
            'role': session['role']
        })
    else:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        
        if not all([name, email, message]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Insert feedback into the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
    except Exception as e:
        app.logger.error(f"Error in /api/feedback: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal error occurred while submitting feedback.'}), 500

# ----------------------------
# Integrate Gemini Chatbot
# ----------------------------
weather_api = WeatherAPIWrapper()
# The chatbot expects a "fertilizer_db". We can pass the dataframe.
# The chatbot's internal logic for fertilizer is a mock, but this makes it extensible.
app = integrate_chatbot_with_flask(app, crop_model, features, fertilizer_df, weather_api)

# Initialize the database
init_db()


# ----------------------------
# Run the app
# ----------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
