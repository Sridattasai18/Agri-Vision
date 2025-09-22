#!/usr/bin/env python3
"""
AgriVision - Main Application Entry Point
Smart Agriculture Platform for Small and Marginal Farmers
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the Flask app
from backend.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Debug mode is enabled if FLASK_DEBUG is set to '1' or 'true'
    debug_mode = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 't']
    
    if not debug_mode and app.secret_key == 'default_secret_key':
        print(
            "WARNING: Using a default secret key in a production environment is insecure. "
            "Set the FLASK_SECRET_KEY environment variable to a strong, random value.",
            file=sys.stderr
        )

    app.run(host='0.0.0.0', port=port, debug=debug_mode)