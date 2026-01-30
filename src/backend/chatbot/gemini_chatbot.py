import warnings
# Suppress FutureWarning for google.generativeai deprecation
# TODO: Migrate to google.genai package in future updates
# See: https://github.com/google-gemini/deprecated-generative-ai-python
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')

import google.generativeai as genai
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import logging
from flask import request, jsonify, session

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to your Gemini API key.")
genai.configure(api_key=GEMINI_API_KEY)

class PromptFactory:
    """
    Manages the generation of prompts for the Gemini model, ensuring consistency and maintainability.
    """
    @staticmethod
    def _format_history(history: List[Dict[str, str]], turns: int = 3) -> str:
        """Formats the last few turns of conversation history for the prompt."""
        if not history:
            return "No previous conversation."
        
        recent_history = history[-turns:]
        formatted_history = "\n".join(
            [f"User: {turn.get('user', '')}\nAgriBot: {turn.get('bot', '')}" for turn in recent_history]
        )
        return f"This is the recent conversation history:\n{formatted_history}"

    @staticmethod
    def classification(message: str, context: 'ChatContext') -> str:
        history_str = PromptFactory._format_history(context.conversation_history)
        return f"""
        Based on the conversation history and the latest message, classify the user's intent into ONE category.

        {history_str}

        Latest Message: "{message}"
        
        Categories: CROP_RECOMMENDATION, FERTILIZER_ADVICE, WEATHER_INQUIRY, SOIL_MANAGEMENT, DISEASE_PEST, GENERAL_HELP, GREETING.
        Respond with only the category name.
        """

    @staticmethod
    def parameter_extraction(message: str, context: 'ChatContext') -> str:
        history_str = PromptFactory._format_history(context.conversation_history)
        return f"""
        Extract agricultural parameters from the latest message, using the conversation history for context.
        
        {history_str}
        Latest Message: "{message}"
        
        Extract any of these parameters if present: N, P, K, pH, temperature, humidity, rainfall, location, crop.
        Return only valid JSON with found parameters, or an empty JSON object {{}} if none are found.
        Example: {{"N": 90, "P": 40, "location": "Mumbai"}}
        """

    @staticmethod
    def crop_recommendation(message: str, context: 'ChatContext', recommendations: List) -> str:
        return f"""
        Based on the conversation history, generate a friendly, detailed response about these crop recommendations.
        {PromptFactory._format_history(context.conversation_history)}
        Soil Data: {context.soil_data}
        Recommendations: {recommendations}
        Latest User Message: "{message}"
        Explain why these crops are suitable and suggest next steps (e.g., fertilizer advice). Be conversational.
        """

    @staticmethod
    def fertilizer_advice(message: str, context: 'ChatContext', crop: str, fertilizer_info: Dict) -> str:
        return f"""
        Based on the conversation history, create a helpful fertilizer recommendation.
        {PromptFactory._format_history(context.conversation_history)}
        Crop: {crop}
        Current Soil NPK: {context.soil_data}
        Fertilizer Analysis: {fertilizer_info}
        Latest User Message: "{message}"
        Explain the nutrient status, deficiency, and specific fertilizer recommendations. Be practical and actionable.
        """

    @staticmethod
    def weather_inquiry(message: str, context: 'ChatContext', location: str, weather_data: Dict) -> str:
        return f"""
        Based on the conversation history, provide weather-based farming advice.
        {PromptFactory._format_history(context.conversation_history)}
        Location: {location}
        Weather Data: {weather_data}
        Latest User Message: "{message}"
        Include:
        1. Current weather summary
        2. Farming implications of these conditions
        3. Specific recommendations (irrigation, planting, harvesting)
        Keep it practical and actionable for farmers.
        """

    @staticmethod
    def general_query(message: str, context: 'ChatContext') -> str:
        return f"""
        You are an expert agricultural assistant. Based on the conversation history, answer this farming question.
        {PromptFactory._format_history(context.conversation_history)}
        Latest Question: "{message}"
        Provide helpful, practical agricultural advice. Be conversational and specific.
        """

@dataclass
class ChatContext:
    """User conversation context"""
    user_role: str = "user"
    soil_data: Optional[Dict] = None
    location: Optional[str] = None
    last_crop_recommendations: Optional[List] = None
    last_fertilizer_advice: Optional[Dict] = None
    conversation_history: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class AgriVisionChatbot:
    def __init__(self, crop_model, features, fertilizer_db, weather_api):
        """Initialize chatbot with existing AgriVision components"""
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.crop_model = crop_model
        self.fertilizer_db = fertilizer_db
        self.features = features
        self.weather_api = weather_api
        self.prompt_factory = PromptFactory()

    def classify_intent(self, message: str, context: ChatContext) -> str:
        """Classify user intent using Gemini"""
        classification_prompt = self.prompt_factory.classification(message, context)
        
        try:
            response = self.model.generate_content(classification_prompt)
            intent = response.text.strip().upper()
            return intent if intent in ['CROP_RECOMMENDATION', 'FERTILIZER_ADVICE', 
                                      'WEATHER_INQUIRY', 'SOIL_MANAGEMENT', 
                                      'DISEASE_PEST', 'GENERAL_HELP', 'GREETING'] else 'GENERAL_HELP'
        except Exception:
            logging.error("Gemini API call failed during intent classification.", exc_info=True)
            return 'GENERAL_HELP'

    def extract_parameters(self, message: str, context: ChatContext) -> Dict:
        """Extract agricultural parameters from user message"""
        extraction_prompt = self.prompt_factory.parameter_extraction(message, context)
        
        try:
            response = self.model.generate_content(extraction_prompt)
            # Clean response and parse JSON
            json_text = response.text.strip()
            json_text = re.sub(r'```json\n?', '', json_text)
            json_text = re.sub(r'```\n?', '', json_text)
            return json.loads(json_text)
        except Exception:
            logging.error("Gemini API call failed during parameter extraction.", exc_info=True)
            return {}

    def get_crop_recommendations(self, soil_data: Dict) -> Optional[List]:
        """Get crop recommendations using existing ML model"""
        try:
            required_features = self.features
            
            # Normalize keys to lowercase to handle variations like 'pH' vs 'ph'
            soil_data_normalized = {k.lower(): v for k, v in soil_data.items()}
            
            # Check if we have all required features
            if all(key in soil_data_normalized for key in required_features):
                # Prepare data in the correct order for the model
                feature_values = [soil_data_normalized[key] for key in self.features]
                
                # Call existing crop prediction
                predictions = self.crop_model.predict_proba([feature_values])[0]
                crop_names = self.crop_model.classes_
                
                # Get top 3 recommendations
                top_indices = predictions.argsort()[-3:][::-1]
                recommendations = [
                    {
                        'crop': crop_names[i],
                        'probability': round(float(predictions[i]) * 100, 2)
                    }
                    for i in top_indices
                ]
                return recommendations
            return None
        except Exception:
            logging.error("Error in local crop recommendation model.", exc_info=True)
            return None

    def get_fertilizer_advice(self, crop: str, soil_data: Dict) -> Optional[Dict]:
        """Get fertilizer advice using existing fertilizer database"""
        # This method now uses the real recommendation logic from app.py
        try:
            N, P, K = soil_data.get('N'), soil_data.get('P'), soil_data.get('K')
            if N is None or P is None or K is None:
                return {"error": "Missing N, P, or K values in soil data."}

            row = self.fertilizer_db[self.fertilizer_db['Crop'] == crop]
            if row.empty:
                return {"error": f"Crop '{crop}' not found in our fertilizer database."}

            rec_N, rec_P, rec_K = row['N'].values[0], row['P'].values[0], row['K'].values[0]

            n_def = max(0, float(rec_N) - float(N))
            p_def = max(0, float(rec_P) - float(P))
            k_def = max(0, float(rec_K) - float(K))
            max_def = max(n_def, p_def, k_def)

            if max_def == 0:
                return {"message": "Soil nutrients are adequate for this crop.", "type": "balanced"}

            if max_def == n_def:
                return {
                    "type": "Nitrogen", "deficiency": round(n_def, 2),
                    "recommendation": f"Add {round(n_def, 2)} units of Nitrogen fertilizer.",
                    "fertilizer_type": "Urea or Ammonium Nitrate"
                }
            elif max_def == p_def:
                return {
                    "type": "Phosphorus", "deficiency": round(p_def, 2),
                    "recommendation": f"Add {round(p_def, 2)} units of Phosphorus fertilizer.",
                    "fertilizer_type": "DAP or Superphosphate"
                }
            else:
                return {
                    "type": "Potassium", "deficiency": round(k_def, 2),
                    "recommendation": f"Add {round(k_def, 2)} units of Potassium fertilizer.",
                    "fertilizer_type": "Potash or MOP"
                }
        except Exception:
            logging.error("Error in local fertilizer advice logic.", exc_info=True)
            return None

    def get_weather_data(self, location: str) -> Optional[Dict]:
        """Get weather data using existing weather API"""
        try:
            # Integrate with your existing weather API
            weather_data = self.weather_api.get_current_weather(location)
            return weather_data
        except Exception:
            logging.error("Error fetching weather data.", exc_info=True)
            return None

    def generate_response(self, message: str, context: ChatContext) -> Dict[str, Any]:
        """Generate intelligent response using Gemini"""
        intent = self.classify_intent(message, context)
        extracted_params = self.extract_parameters(message, context)
        
        # Update context with new parameters
        if context.soil_data:
            context.soil_data.update(extracted_params)
        else:
            context.soil_data = extracted_params
            
        # Update location if provided
        if 'location' in extracted_params:
            context.location = extracted_params['location']

        response_data = {
            'response': '',
            'actions': [],
            'data': {},
            'suggestions': []
        }

        # Handle different intents
        if intent == 'GREETING':
            response_data = self._handle_greeting(context)
            
        elif intent == 'CROP_RECOMMENDATION':
            response_data = self._handle_crop_recommendation(message, context)
            
        elif intent == 'FERTILIZER_ADVICE':
            response_data = self._handle_fertilizer_advice(message, context)
            
        elif intent == 'WEATHER_INQUIRY':
            response_data = self._handle_weather_inquiry(message, context)
            
        else:
            response_data = self._handle_general_query(message, context)

        # Add conversation to history
        context.conversation_history.append({
            'user': message,
            'bot': response_data['response'],
            'timestamp': datetime.now().isoformat(),
            'intent': intent
        })

        return response_data

    def _handle_greeting(self, context: ChatContext) -> Dict:
        """Handle greeting messages"""
        role_specific = {
            'farmer': "Hello! I'm AgriBot, your farming assistant. I can help you with crop recommendations, fertilizer advice, and weather-based farming guidance.",
            'officer': "Greetings! I'm AgriBot, ready to assist with agricultural analysis, crop planning, and technical recommendations.",
            'user': "Hi there! I'm AgriBot, your agricultural assistant. Ask me about crops, farming, weather, or soil management!"
        }
        greeting = role_specific.get(context.user_role, role_specific['user'])
        response_text = f"{greeting}\n\nWhat would you like to know about today? \U0001F33E"

        return {
            'response': response_text,
            'actions': ['greeting'],
            'data': {},
            'suggestions': ['Recommend a crop', 'Weather in my city', 'How to improve soil?']
        }

    def _handle_crop_recommendation(self, message: str, context: ChatContext) -> Dict:
        """Handle crop recommendation queries"""
        if not context.soil_data:
            return {
                'response': "I'd love to recommend the best crops for you! Could you share your soil details?\n\nI need:\n• Nitrogen (N) level\n• Phosphorus (P) level\n• Potassium (K) level\n• Soil pH\n• Average temperature\n• Humidity level\n• Expected rainfall\n\nExample: 'My soil has N-90, P-40, K-50, pH-6.5, temperature 25°C, humidity 80%, rainfall 200mm'",
                'actions': ['request_soil_data'],
                'suggestions': ['Get Soil Test', 'Enter Soil Data', 'Weather Check']
            }

        # Check if we have enough data for prediction
        required_params = ['N', 'P', 'K', 'temperature', 'humidity', 'rainfall']
        missing_params = [p for p in required_params if p not in context.soil_data]
        
        if missing_params:
            return {
                'response': f"I need a bit more information to give you accurate recommendations.\n\nMissing: {', '.join(missing_params)}\n\nCould you provide these values?",
                'actions': ['request_missing_data'],
                'data': {'missing_params': missing_params}
            }

        # Get crop recommendations
        recommendations = self.get_crop_recommendations(context.soil_data)
        context.last_crop_recommendations = recommendations

        if not recommendations:
            return {
                'response': "I'm having trouble analyzing your soil data right now. Please check your values and try again.",
                'actions': ['retry_analysis']
            }

        # Generate detailed response using Gemini
        detailed_prompt = self.prompt_factory.crop_recommendation(message, context, recommendations)
        
        try:
            gemini_response = self.model.generate_content(detailed_prompt)
            detailed_response = gemini_response.text
        except Exception as e:
            # Fallback response
            logging.error(f"Gemini API call failed in _handle_crop_recommendation: {e}", exc_info=True)
            crop_list = [f"{rec['crop']} ({rec['probability']}% suitable)" for rec in recommendations]
            detailed_response = f"Based on your soil analysis, here are my top recommendations:\n\n{chr(10).join(crop_list)}\n\nThese crops match well with your soil's NPK levels and environmental conditions!"

        return {
            'response': detailed_response,
            'actions': ['show_crop_details', 'get_fertilizer_advice'],
            'data': {'recommendations': recommendations},
            'suggestions': ['Fertilizer Advice', 'Weather Update', 'Soil Tips']
        }

    def _handle_fertilizer_advice(self, message: str, context: ChatContext) -> Dict:
        """Handle fertilizer advice queries"""
        # Extract crop from message or use last recommendation
        crop = None
        if 'crop' in context.soil_data:
            crop = context.soil_data['crop']
        elif context.last_crop_recommendations:
            crop = context.last_crop_recommendations[0]['crop']

        if not crop:
            return {
                'response': "Which crop would you like fertilizer advice for? You can mention the crop name or I can suggest based on your soil conditions.",
                'actions': ['request_crop_selection'],
                'suggestions': ['Recommend Crops First', 'Rice Fertilizer', 'Wheat Fertilizer']
            }

        if not context.soil_data or not any(k in context.soil_data for k in ['N', 'P', 'K']):
            return {
                'response': f"To give you the best fertilizer advice for {crop}, I need your current soil NPK levels.\n\nCould you share:\n• Nitrogen (N) level\n• Phosphorus (P) level\n• Potassium (K) level",
                'actions': ['request_npk_data'],
                'suggestions': ['Get Soil Test', 'Skip to General Advice']
            }

        # Get fertilizer recommendations
        fertilizer_info = self.get_fertilizer_advice(crop, context.soil_data)
        context.last_fertilizer_advice = fertilizer_info

        if not fertilizer_info:
            return {
                'response': f"I'm working on fertilizer recommendations for {crop}. This feature is being enhanced!",
                'actions': ['feature_development']
            }

        # Generate detailed fertilizer response
        fertilizer_prompt = self.prompt_factory.fertilizer_advice(message, context, crop, fertilizer_info)
        
        try:
            gemini_response = self.model.generate_content(fertilizer_prompt)
            detailed_response = gemini_response.text
        except Exception as e:
            # Fallback response
            logging.error(f"Gemini API call failed in _handle_fertilizer_advice: {e}", exc_info=True)
            if fertilizer_info.get("type") == "balanced":
                detailed_response = fertilizer_info.get("message", "Your soil seems balanced for this crop.")
            else:
                detailed_response = f"For your {crop} crop, you have a {fertilizer_info.get('type')} deficiency of {fertilizer_info.get('deficiency')} units. It is recommended to use {fertilizer_info.get('fertilizer_type')}."

        return {
            'response': detailed_response,
            'actions': ['show_fertilizer_details'],
            'data': {'fertilizer_info': fertilizer_info},
            'suggestions': ['Weather Check', 'Soil Improvement', 'Crop Care Tips']
        }

    def _handle_weather_inquiry(self, message: str, context: ChatContext) -> Dict:
        """Handle weather-related queries"""
        location = context.location or context.soil_data.get('location') if context.soil_data else None
        
        if not location:
            return {
                'response': "Which location would you like weather information for? Please mention your city or region.",
                'actions': ['request_location'],
                'suggestions': ['Mumbai Weather', 'Delhi Weather', 'Bangalore Weather']
            }

        # Get weather data
        weather_data = self.get_weather_data(location)
        
        if not weather_data:
            return {
                'response': f"I'm having trouble getting weather data for {location} right now. Please try again in a moment.",
                'actions': ['retry_weather']
            }

        # Generate weather-based farming advice
        weather_prompt = self.prompt_factory.weather_inquiry(message, context, location, weather_data)
        
        try:
            gemini_response = self.model.generate_content(weather_prompt)
            detailed_response = gemini_response.text
        except Exception as e:
            # Fallback response
            logging.error(f"Gemini API call failed in _handle_weather_inquiry: {e}", exc_info=True)
            temp = weather_data.get('temperature', 'N/A')
            humidity = weather_data.get('humidity', 'N/A')
            detailed_response = f"Weather in {location}:\n• Temperature: {temp}°C\n• Humidity: {humidity}%\n\nThis is good weather for most farming activities. Consider irrigation if humidity is low."

        return {
            'response': detailed_response,
            'actions': ['show_weather_details'],
            'data': {'weather': weather_data},
            'suggestions': ['Irrigation Advice', 'Crop Protection', 'Harvest Timing']
        }

    def _handle_general_query(self, message: str, context: ChatContext) -> Dict:
        """Handle general agricultural queries"""
        general_prompt = self.prompt_factory.general_query(message, context)
        
        try:
            gemini_response = self.model.generate_content(general_prompt)
            response_text = gemini_response.text
        except Exception as e:
            logging.error(f"Gemini API call failed in _handle_general_query: {e}", exc_info=True)
            response_text = "I'm sorry, I'm having a little trouble connecting to my knowledge base right now. Please check your API key and network connection, then try asking your question again in a moment."

        return {
            'response': response_text,
            'actions': ['general_advice'],
            'suggestions': ['Crop Recommendations', 'Fertilizer Advice', 'Weather Check', 'Platform Help']
        }


# Flask integration for AgriVision
def integrate_chatbot_with_flask(app, crop_model, features, fertilizer_db, weather_api):
    """Integrate chatbot with existing Flask app"""
    
    # Store chatbot instance and user contexts
    app.chatbot = AgriVisionChatbot(crop_model, features, fertilizer_db, weather_api)
    app.user_contexts = {}  # Store contexts by session ID
    
    @app.route('/api/chatbot', methods=['POST'])
    def chatbot_endpoint():
        try:
            data = request.get_json()
            message = data.get('message', '').strip()
            session_id = session.get('user', 'anonymous')  # Use username for unique session
            
            if not message:
                return jsonify({'error': 'No message provided'}), 400
            
            # Get or create user context
            if session_id not in app.user_contexts:
                app.user_contexts[session_id] = ChatContext(
                    user_role=session.get('role', 'user')
                )
            
            context = app.user_contexts[session_id]
            
            # Update context with any provided data
            if 'soil_data' in data:
                context.soil_data = data['soil_data']
            if 'location' in data:
                context.location = data['location']
            
            # Generate response
            response_data = app.chatbot.generate_response(message, context)
            
            return jsonify({
                'success': True,
                'response': response_data['response'],
                'actions': response_data.get('actions', []),
                'data': response_data.get('data', {}),
                'suggestions': response_data.get('suggestions', []),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logging.error(f"Error in /api/chatbot endpoint: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Chatbot service temporarily unavailable',
                'details': str(e)
            }), 500
    
    @app.route('/api/chatbot/context', methods=['GET', 'POST'])
    def chatbot_context():
        """Manage chatbot context"""
        session_id = session.get('user', 'anonymous')
        
        if request.method == 'GET':
            # Get current context
            context = app.user_contexts.get(session_id)
            if context:
                return jsonify({
                    'soil_data': context.soil_data,
                    'location': context.location,
                    'conversation_count': len(context.conversation_history)
                })
            return jsonify({'message': 'No context found'})
        
        elif request.method == 'POST':
            # Update context
            data = request.get_json()
            if session_id not in app.user_contexts:
                app.user_contexts[session_id] = ChatContext(
                    user_role=session.get('role', 'user')
                )
            
            context = app.user_contexts[session_id]
            if 'soil_data' in data:
                context.soil_data = data['soil_data']
            if 'location' in data:
                context.location = data['location']
            
            return jsonify({'success': True, 'message': 'Context updated'})
    
    return app

# Example usage in your main app.py:
"""
from src.backend.chatbot.gemini_chatbot import integrate_chatbot_with_flask

# After initializing your Flask app and loading models
app = integrate_chatbot_with_flask(app, crop_model, features, fertilizer_db, weather_api)
"""
