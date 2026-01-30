"""
Example Flask routes for plant disease detection
Add these to your existing Flask app
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from disease_service import init_detector, get_detector

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads/plant_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize detector when app starts
init_detector(
    model_path='models/plant_disease/plant_disease_model_1_latest.pt',
    disease_info_path='models/plant_disease/disease_info.csv',
    supplement_info_path='models/plant_disease/supplement_info.csv'
)


@app.route('/api/plant-disease/predict', methods=['POST'])
def predict_plant_disease():
    """
    Endpoint to predict plant disease from uploaded image
    
    Request: multipart/form-data with 'image' file
    Response: JSON with prediction results
    
    Example usage:
        curl -X POST -F "image=@leaf.jpg" http://localhost:5000/api/plant-disease/predict
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # Get prediction
            detector = get_detector()
            result = detector.predict_from_path(filepath)
            
            # Optional: Delete temporary file after prediction
            # os.remove(filepath)
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400


@app.route('/api/plant-disease/predict-direct', methods=['POST'])
def predict_plant_disease_direct():
    """
    Endpoint to predict disease without saving file to disk
    Faster for temporary predictions
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        # Predict directly from file object
        detector = get_detector()
        result = detector.predict_from_file(file)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plant-disease/diseases', methods=['GET'])
def get_all_diseases():
    """
    Endpoint to get list of all detectable diseases
    
    Example usage:
        curl http://localhost:5000/api/plant-disease/diseases
    """
    try:
        detector = get_detector()
        diseases = detector.get_all_diseases()
        return jsonify({
            'success': True,
            'data': diseases,
            'count': len(diseases)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plant-disease/supplements', methods=['GET'])
def get_all_supplements():
    """
    Endpoint to get list of all available supplements
    
    Example usage:
        curl http://localhost:5000/api/plant-disease/supplements
    """
    try:
        detector = get_detector()
        supplements = detector.get_all_supplements()
        return jsonify({
            'success': True,
            'data': supplements,
            'count': len(supplements)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plant-disease/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the service is running
    """
    try:
        detector = get_detector()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'message': 'Plant disease detection service is running'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
