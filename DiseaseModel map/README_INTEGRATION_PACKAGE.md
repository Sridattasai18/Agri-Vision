# Plant Disease Detection - Integration Package

This package contains everything you need to integrate the plant disease detection feature into your existing Flask project.

## 📦 Package Contents

### Core Files (Ready to Use)
1. **plant_disease_model.py** - CNN model architecture
2. **disease_service.py** - Prediction service with easy-to-use API
3. **flask_routes_example.py** - Complete Flask route examples
4. **test_integration.py** - Test script to verify setup

### Documentation
5. **INTEGRATION_GUIDE.txt** - Comprehensive integration guide (READ THIS FIRST)
6. **SETUP_CHECKLIST.md** - Step-by-step setup checklist
7. **requirements_minimal.txt** - Required Python packages
8. **README_INTEGRATION_PACKAGE.md** - This file

## 🚀 Quick Start (5 Minutes)

### 1. Copy Files to Your Project
```
your_project/
├── models/plant_disease/
│   ├── plant_disease_model.py      ← Copy from this package
│   ├── disease_service.py          ← Copy from this package
│   ├── disease_info.csv            ← Copy from original project
│   ├── supplement_info.csv         ← Copy from original project
│   └── plant_disease_model_1_latest.pt  ← Download (see below)
```

### 2. Download Model File
Download `plant_disease_model_1_latest.pt` (~100MB) from:
https://drive.google.com/drive/folders/1ewJWAiduGuld_9oGSrTuLumg9y62qS6A?usp=share_link

### 3. Install Dependencies
```bash
pip install torch==1.8.1+cpu torchvision==0.9.1+cpu Pillow==8.2.0 numpy==1.20.2 pandas==1.2.4
```

### 4. Initialize in Your Flask App
```python
from models.plant_disease.disease_service import init_detector

# Initialize once when app starts
init_detector(
    model_path='models/plant_disease/plant_disease_model_1_latest.pt',
    disease_info_path='models/plant_disease/disease_info.csv',
    supplement_info_path='models/plant_disease/supplement_info.csv'
)
```

### 5. Add a Route
```python
from models.plant_disease.disease_service import get_detector

@app.route('/api/plant-disease/predict', methods=['POST'])
def predict():
    file = request.files['image']
    detector = get_detector()
    result = detector.predict_from_path(file)
    return jsonify(result)
```

### 6. Test It
```bash
python test_integration.py
```

## 📚 What Each File Does

### plant_disease_model.py
- Contains the CNN architecture (4 convolutional blocks)
- Defines 39 disease classes
- Pure PyTorch model definition
- No dependencies on Flask or web framework

### disease_service.py
- Wraps the model with easy-to-use methods
- Handles image preprocessing
- Returns structured prediction results
- Manages disease and supplement information
- Thread-safe singleton pattern

### flask_routes_example.py
- Complete working Flask application
- 5 ready-to-use API endpoints:
  - `/api/plant-disease/predict` - Main prediction endpoint
  - `/api/plant-disease/predict-direct` - Faster prediction (no disk save)
  - `/api/plant-disease/diseases` - List all diseases
  - `/api/plant-disease/supplements` - List all supplements
  - `/api/plant-disease/health` - Health check
- Includes error handling and validation
- Copy routes to your existing Flask app

### test_integration.py
- Verifies all dependencies are installed
- Tests model loading
- Tests service initialization
- Optional full integration test with actual prediction
- Run with `--full` flag for complete test

## 🎯 Usage Examples

### Example 1: Simple Prediction
```python
from disease_service import get_detector

detector = get_detector()
result = detector.predict_from_path('leaf_image.jpg')

print(f"Disease: {result['disease_name']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Example 2: API Endpoint
```python
@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    detector = get_detector()
    result = detector.predict_from_file(file)
    return jsonify({'success': True, 'data': result})
```

### Example 3: Get All Diseases
```python
detector = get_detector()
diseases = detector.get_all_diseases()
print(f"Can detect {len(diseases)} diseases")
```

## 📊 API Response Format

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

## 🔧 Integration Patterns

### Pattern 1: Microservice Style
Keep disease detection as a separate module:
```
your_project/
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── main_routes.py
│   │   └── disease_routes.py  ← Add disease detection routes here
│   └── services/
│       └── plant_disease/     ← Put model files here
```

### Pattern 2: Monolithic Style
Integrate directly into existing structure:
```
your_project/
├── models/
│   ├── user_model.py
│   └── plant_disease_model.py  ← Add here
├── services/
│   ├── auth_service.py
│   └── disease_service.py      ← Add here
└── routes/
    ├── api.py                  ← Add routes here
```

### Pattern 3: Blueprint Style (Recommended for Large Projects)
```python
# disease_blueprint.py
from flask import Blueprint
from disease_service import get_detector

disease_bp = Blueprint('disease', __name__, url_prefix='/api/disease')

@disease_bp.route('/predict', methods=['POST'])
def predict():
    # ... prediction logic
    pass

# In main app
app.register_blueprint(disease_bp)
```

## ⚙️ Configuration Options

### Use GPU Instead of CPU
```python
# In disease_service.py, change:
torch.load(model_path, map_location=torch.device('cpu'))
# To:
torch.load(model_path, map_location=torch.device('cuda'))

# And install GPU version:
pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111
```

### Adjust Image Size
```python
# In disease_service.py, change:
image = image.resize((224, 224))
# To your preferred size (must match model training)
```

### Add Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def predict_cached(image_hash):
    # Cache predictions for repeated images
    pass
```

## 🐛 Troubleshooting

### "Model file not found"
- Ensure you downloaded the .pt file from Google Drive
- Check the path in `init_detector()` matches actual location
- Use absolute paths if relative paths don't work

### "Import error: No module named 'torch'"
```bash
pip install torch==1.8.1+cpu torchvision==0.9.1+cpu
```

### "Detector not initialized"
- Call `init_detector()` before using `get_detector()`
- Initialize in app startup, not in route handlers

### "Out of memory"
- Model requires ~500MB RAM
- Use CPU version for smaller footprint
- Close other applications
- Consider using GPU

### Slow predictions
- First prediction is slow (model loading)
- Subsequent predictions are faster (~100-200ms)
- Use GPU for 10x speed improvement
- Consider batch processing for multiple images

## 📈 Performance Tips

1. **Initialize Once**: Call `init_detector()` once at app startup, not per request
2. **Use GPU**: 10x faster inference with CUDA-enabled GPU
3. **Batch Processing**: Process multiple images together
4. **Caching**: Cache predictions for identical images
5. **Async Processing**: Use Celery for background processing
6. **Load Balancing**: Use multiple workers with Gunicorn

## 🔒 Security Considerations

1. **File Validation**: Always validate uploaded files
2. **Size Limits**: Set max file size (10MB recommended)
3. **File Types**: Only allow image types (png, jpg, jpeg)
4. **Sanitization**: Use `secure_filename()` for file names
5. **Rate Limiting**: Prevent abuse with rate limits
6. **Authentication**: Add auth if needed

## 📝 Files You Still Need

From the original project, copy these files:
1. `disease_info.csv` - Located in `Plant-Disease-Detection-main/Flask Deployed App/`
2. `supplement_info.csv` - Located in `Plant-Disease-Detection-main/Flask Deployed App/`

Download this file:
3. `plant_disease_model_1_latest.pt` - From Google Drive link above

## 🎓 Learn More

- **Original Project**: Plant-Disease-Detection-main/
- **Blog Post**: https://medium.com/analytics-vidhya/plant-disease-detection-using-convolutional-neural-networks-and-pytorch-87c00c54c88f
- **PyTorch Docs**: https://pytorch.org/docs/
- **Flask Docs**: https://flask.palletsprojects.com/

## 💡 Next Steps

1. ✅ Read `INTEGRATION_GUIDE.txt` for detailed instructions
2. ✅ Follow `SETUP_CHECKLIST.md` step by step
3. ✅ Run `test_integration.py` to verify setup
4. ✅ Copy routes from `flask_routes_example.py`
5. ✅ Test with curl or Postman
6. ✅ Integrate into your UI
7. ✅ Deploy to production

## 🤝 Support

If you encounter issues:
1. Check `INTEGRATION_GUIDE.txt` for detailed troubleshooting
2. Run `test_integration.py` to identify the problem
3. Verify all files are in correct locations
4. Check that all dependencies are installed

## 📄 License

This integration package is based on the open-source Plant Disease Detection project.
Refer to the original project for license information.

---

**Ready to integrate?** Start with `SETUP_CHECKLIST.md` for a step-by-step guide!
