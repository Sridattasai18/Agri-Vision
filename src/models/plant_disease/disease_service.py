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
from .plant_disease_model import PlantDiseaseCNN, DISEASE_CLASSES


class PlantDiseaseDetector:
    """
    Service class for plant disease detection
    """
    
    def __init__(self, model_path, disease_info_path, supplement_info_path):
        """
        Initialize the disease detector
        """
        self.model = PlantDiseaseCNN(num_classes=39)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        
        # Load disease and supplement information
        self.disease_info = pd.read_csv(disease_info_path, encoding='cp1252').fillna('')
        self.supplement_info = pd.read_csv(supplement_info_path, encoding='cp1252').fillna('')
        
        # Define preprocessing transforms
        try:
            from torchvision import transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        except ImportError:
            # Fallback if imports fail (should not happen given requirements)
            import torchvision.transforms as transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

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
        Internal prediction method with robust preprocessing
        """
        try:
            # 1. Ensure RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 2. Apply transforms
            input_data = self.transform(image)
            
            # 3. Add batch dimension
            input_data = input_data.unsqueeze(0)
            
            # 4. Make prediction
            with torch.no_grad():
                output = self.model(input_data)
                probabilities = torch.nn.functional.softmax(output, dim=1)
                confidence, pred_index = torch.max(probabilities, dim=1)
                pred_index = int(pred_index.item())
                confidence = float(confidence.item())
            
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
                'prediction_index': pred_index,
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
        except Exception as e:
            # Re-raise exception to be caught by the API endpoint
            # But print it first for debugging
            print(f"Prediction Error Details: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
    
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
