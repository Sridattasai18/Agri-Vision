"""
Plant Disease Detection Service
Handles model loading, prediction, and result formatting
"""

import os
import torch
import numpy as np
import pandas as pd
from PIL import Image
import torchvision.transforms.functional as TF
from plant_disease_model import PlantDiseaseCNN, DISEASE_CLASSES


class PlantDiseaseDetector:
    """
    Service class for plant disease detection
    """
    
    def __init__(self, model_path, disease_info_path, supplement_info_path):
        """
        Initialize the disease detector
        
        Args:
            model_path: Path to the .pt model file
            disease_info_path: Path to disease_info.csv
            supplement_info_path: Path to supplement_info.csv
        """
        self.model = PlantDiseaseCNN(num_classes=39)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        
        # Load disease and supplement information
        self.disease_info = pd.read_csv(disease_info_path, encoding='cp1252')
        self.supplement_info = pd.read_csv(supplement_info_path, encoding='cp1252')
    
    def predict_from_path(self, image_path):
        """
        Predict disease from image file path
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: Prediction results with disease info
        """
        image = Image.open(image_path)
        return self._predict(image)
    
    def predict_from_file(self, file_object):
        """
        Predict disease from uploaded file object
        
        Args:
            file_object: File object from request.files
            
        Returns:
            dict: Prediction results with disease info
        """
        image = Image.open(file_object)
        return self._predict(image)
    
    def _predict(self, image):
        """
        Internal prediction method
        
        Args:
            image: PIL Image object
            
        Returns:
            dict: Complete prediction results
        """
        # Preprocess image
        image = image.resize((224, 224))
        input_data = TF.to_tensor(image)
        input_data = input_data.view((-1, 3, 224, 224))
        
        # Make prediction
        with torch.no_grad():
            output = self.model(input_data)
            output = output.detach().numpy()
            pred_index = np.argmax(output)
            confidence = float(np.max(output))
        
        # Get disease information
        disease_name = self.disease_info['disease_name'][pred_index]
        description = self.disease_info['description'][pred_index]
        prevention_steps = self.disease_info['Possible Steps'][pred_index]
        image_url = self.disease_info['image_url'][pred_index]
        
        # Get supplement information
        supplement_name = self.supplement_info['supplement name'][pred_index]
        supplement_image = self.supplement_info['supplement image'][pred_index]
        supplement_buy_link = self.supplement_info['buy link'][pred_index]
        
        return {
            'prediction_index': int(pred_index),
            'disease_class': DISEASE_CLASSES[pred_index],
            'disease_name': disease_name,
            'description': description,
            'prevention_steps': prevention_steps,
            'image_url': image_url,
            'confidence': confidence,
            'supplement': {
                'name': supplement_name,
                'image': supplement_image,
                'buy_link': supplement_buy_link
            }
        }
    
    def get_all_diseases(self):
        """
        Get list of all detectable diseases
        
        Returns:
            list: List of disease names
        """
        return list(self.disease_info['disease_name'])
    
    def get_all_supplements(self):
        """
        Get list of all available supplements
        
        Returns:
            list: List of supplement information
        """
        return self.supplement_info.to_dict('records')


# Global detector instance (initialize once)
detector = None


def init_detector(model_path, disease_info_path, supplement_info_path):
    """
    Initialize the global detector instance
    Call this once when your Flask app starts
    """
    global detector
    detector = PlantDiseaseDetector(model_path, disease_info_path, supplement_info_path)
    return detector


def get_detector():
    """
    Get the global detector instance
    """
    if detector is None:
        raise RuntimeError("Detector not initialized. Call init_detector() first.")
    return detector
