"""
Test script to verify plant disease detection integration
Run this after setting up all files to ensure everything works
"""

import os
import sys


def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import torch
        print("✓ PyTorch installed:", torch.__version__)
    except ImportError:
        print("✗ PyTorch not installed. Run: pip install torch==1.8.1+cpu")
        return False
    
    try:
        import torchvision
        print("✓ TorchVision installed:", torchvision.__version__)
    except ImportError:
        print("✗ TorchVision not installed. Run: pip install torchvision==0.9.1+cpu")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow installed")
    except ImportError:
        print("✗ Pillow not installed. Run: pip install Pillow==8.2.0")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy installed:", np.__version__)
    except ImportError:
        print("✗ NumPy not installed. Run: pip install numpy==1.20.2")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas installed:", pd.__version__)
    except ImportError:
        print("✗ Pandas not installed. Run: pip install pandas==1.2.4")
        return False
    
    return True


def test_model_files():
    """Test if required model files exist"""
    print("\nTesting model files...")
    
    files_to_check = [
        'plant_disease_model.py',
        'disease_service.py',
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✓ {file} found")
        else:
            print(f"✗ {file} not found")
            all_exist = False
    
    return all_exist


def test_model_loading():
    """Test if model can be loaded"""
    print("\nTesting model loading...")
    
    try:
        from plant_disease_model import PlantDiseaseCNN, DISEASE_CLASSES
        print("✓ Model class imported successfully")
        
        model = PlantDiseaseCNN(num_classes=39)
        print("✓ Model instantiated successfully")
        
        print(f"✓ Disease classes loaded: {len(DISEASE_CLASSES)} classes")
        
        return True
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False


def test_service():
    """Test if service can be initialized (without actual model file)"""
    print("\nTesting service...")
    
    try:
        from disease_service import PlantDiseaseDetector
        print("✓ Service class imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing service: {e}")
        return False


def test_full_integration(model_path, disease_info_path, supplement_info_path, test_image_path):
    """Test full integration with actual files"""
    print("\nTesting full integration...")
    
    # Check if files exist
    if not os.path.exists(model_path):
        print(f"✗ Model file not found: {model_path}")
        print("  Download from: https://drive.google.com/drive/folders/1ewJWAiduGuld_9oGSrTuLumg9y62qS6A")
        return False
    
    if not os.path.exists(disease_info_path):
        print(f"✗ Disease info file not found: {disease_info_path}")
        return False
    
    if not os.path.exists(supplement_info_path):
        print(f"✗ Supplement info file not found: {supplement_info_path}")
        return False
    
    if not os.path.exists(test_image_path):
        print(f"✗ Test image not found: {test_image_path}")
        print("  Please provide a test leaf image")
        return False
    
    try:
        from disease_service import init_detector, get_detector
        
        print("✓ Initializing detector...")
        init_detector(model_path, disease_info_path, supplement_info_path)
        
        print("✓ Getting detector instance...")
        detector = get_detector()
        
        print("✓ Making prediction...")
        result = detector.predict_from_path(test_image_path)
        
        print("\n" + "="*60)
        print("PREDICTION RESULT:")
        print("="*60)
        print(f"Disease: {result['disease_name']}")
        print(f"Class: {result['disease_class']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Description: {result['description'][:100]}...")
        print(f"Supplement: {result['supplement']['name']}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"✗ Error during integration test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("PLANT DISEASE DETECTION - INTEGRATION TEST")
    print("="*60)
    
    # Basic tests
    if not test_imports():
        print("\n❌ Import test failed. Install missing packages.")
        return
    
    if not test_model_files():
        print("\n❌ Model files test failed. Copy required files.")
        return
    
    if not test_model_loading():
        print("\n❌ Model loading test failed. Check model code.")
        return
    
    if not test_service():
        print("\n❌ Service test failed. Check service code.")
        return
    
    print("\n" + "="*60)
    print("BASIC TESTS PASSED ✓")
    print("="*60)
    
    # Full integration test (optional)
    print("\nTo test full integration with actual model and data:")
    print("Run: python test_integration.py --full")
    print("\nRequired files:")
    print("  - plant_disease_model_1_latest.pt (download from Google Drive)")
    print("  - disease_info.csv")
    print("  - supplement_info.csv")
    print("  - test_image.jpg (any plant leaf image)")
    
    # Check if full test requested
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        print("\n" + "="*60)
        print("RUNNING FULL INTEGRATION TEST")
        print("="*60)
        
        # Update these paths based on your setup
        model_path = 'plant_disease_model_1_latest.pt'
        disease_info_path = 'disease_info.csv'
        supplement_info_path = 'supplement_info.csv'
        test_image_path = 'test_image.jpg'
        
        if test_full_integration(model_path, disease_info_path, supplement_info_path, test_image_path):
            print("\n✅ FULL INTEGRATION TEST PASSED!")
        else:
            print("\n❌ FULL INTEGRATION TEST FAILED")


if __name__ == '__main__':
    main()
