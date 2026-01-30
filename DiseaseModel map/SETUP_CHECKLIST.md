# Plant Disease Detection - Integration Checklist

## Quick Setup Guide

### ✅ Step 1: Copy Files
Copy these files from this directory to your project:

```
your_project/
├── models/plant_disease/
│   ├── plant_disease_model.py      ✓ Copy this file
│   ├── disease_service.py          ✓ Copy this file
│   ├── disease_info.csv            ✓ Copy from original project
│   └── supplement_info.csv         ✓ Copy from original project
```

### ✅ Step 2: Download Model File
- [ ] Download `plant_disease_model_1_latest.pt` from:
  - https://drive.google.com/drive/folders/1ewJWAiduGuld_9oGSrTuLumg9y62qS6A?usp=share_link
- [ ] Place it in `models/plant_disease/` folder
- [ ] File size should be ~100MB

### ✅ Step 3: Install Dependencies
```bash
pip install torch==1.8.1+cpu torchvision==0.9.1+cpu Pillow==8.2.0 numpy==1.20.2 pandas==1.2.4
```

Or add to your requirements.txt:
```
torch==1.8.1+cpu
torchvision==0.9.1+cpu
Pillow==8.2.0
numpy==1.20.2
pandas==1.2.4
```

### ✅ Step 4: Initialize in Your Flask App
Add to your main app file (e.g., `app.py` or `__init__.py`):

```python
from models.plant_disease.disease_service import init_detector

# After creating Flask app
app = Flask(__name__)

# Initialize detector
init_detector(
    model_path='models/plant_disease/plant_disease_model_1_latest.pt',
    disease_info_path='models/plant_disease/disease_info.csv',
    supplement_info_path='models/plant_disease/supplement_info.csv'
)
```

### ✅ Step 5: Add Routes
Copy routes from `flask_routes_example.py` to your Flask app, or use them as reference.

Minimum required route:
```python
from disease_service import get_detector

@app.route('/api/plant-disease/predict', methods=['POST'])
def predict_plant_disease():
    file = request.files['image']
    detector = get_detector()
    result = detector.predict_from_path(file)
    return jsonify(result)
```

### ✅ Step 6: Test
Test with curl:
```bash
curl -X POST -F "image=@test_leaf.jpg" http://localhost:5000/api/plant-disease/predict
```

Or use Postman:
- Method: POST
- URL: http://localhost:5000/api/plant-disease/predict
- Body: form-data
- Key: image (type: File)
- Value: Select a leaf image

---

## Files You Need

### From This Directory (Created for you):
1. ✅ `plant_disease_model.py` - CNN model architecture
2. ✅ `disease_service.py` - Prediction service
3. ✅ `flask_routes_example.py` - Example Flask routes
4. ✅ `requirements_minimal.txt` - Dependencies
5. ✅ `INTEGRATION_GUIDE.txt` - Complete documentation

### From Original Project:
6. ⬜ `disease_info.csv` - Located in `Plant-Disease-Detection-main/Flask Deployed App/`
7. ⬜ `supplement_info.csv` - Located in `Plant-Disease-Detection-main/Flask Deployed App/`

### Download Required:
8. ⬜ `plant_disease_model_1_latest.pt` - Download from Google Drive

---

## Expected API Response

```json
{
  "success": true,
  "data": {
    "prediction_index": 29,
    "disease_class": "Tomato___Bacterial_spot",
    "disease_name": "Tomato Bacterial Spot",
    "description": "Bacterial spot is caused by...",
    "prevention_steps": "Use disease-free seeds...",
    "image_url": "https://example.com/image.jpg",
    "confidence": 0.95,
    "supplement": {
      "name": "Copper Fungicide",
      "image": "https://example.com/product.jpg",
      "buy_link": "https://example.com/buy"
    }
  }
}
```

---

## Troubleshooting

### Model file not found
- Ensure you downloaded the .pt file
- Check the path in init_detector() matches actual file location

### Import errors
- Run: `pip install -r requirements_minimal.txt`
- Ensure torch and torchvision are installed

### Prediction errors
- Verify image is valid (PNG, JPG, JPEG)
- Check image file size (< 10MB recommended)
- Ensure image contains plant leaves

### Memory issues
- Model requires ~500MB RAM
- Use CPU version for smaller memory footprint
- Consider GPU version for production

---

## Production Considerations

- [ ] Add rate limiting to prediction endpoint
- [ ] Implement caching for repeated predictions
- [ ] Add logging for predictions and errors
- [ ] Set up monitoring for model performance
- [ ] Consider using GPU for faster inference
- [ ] Implement batch prediction for multiple images
- [ ] Add authentication if needed
- [ ] Set up proper error handling and validation

---

## Support

For detailed documentation, see `INTEGRATION_GUIDE.txt`

For original project details:
- GitHub: Plant-Disease-Detection-main/
- Blog: https://medium.com/analytics-vidhya/plant-disease-detection-using-convolutional-neural-networks-and-pytorch-87c00c54c88f
