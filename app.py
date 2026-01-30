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

# Validate required environment variables
required_env_vars = ['GEMINI_API_KEY', 'OPENWEATHER_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print("\n" + "="*60, file=sys.stderr)
    print("❌ ERROR: Missing Required Environment Variables", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"\nThe following environment variables are not set:", file=sys.stderr)
    for var in missing_vars:
        print(f"  - {var}", file=sys.stderr)
    print("\n📝 To fix this:", file=sys.stderr)
    print("  1. Copy .env.example to .env", file=sys.stderr)
    print("  2. Add your actual API keys to .env", file=sys.stderr)
    print("\n🔑 Get API keys from:", file=sys.stderr)
    print("  - Gemini API: https://makersuite.google.com/app/apikey", file=sys.stderr)
    print("  - OpenWeather: https://openweathermap.org/api", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    sys.exit(1)

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