# 🌱 AgriVision - Smart Agriculture Platform

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![ML](https://img.shields.io/badge/ML-scikit--learn-orange.svg)](https://scikit-learn.org/)
[![AI](https://img.shields.io/badge/AI-Google_Gemini-yellow.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **AI-powered platform helping farmers make data-driven decisions**

AgriVision is a comprehensive smart agriculture platform designed for small and marginal farmers. Get intelligent crop recommendations, fertilizer suggestions, real-time weather insights, and AI-powered farming advice—all in one place.

---

## ✨ Features

### 🌾 Crop Recommendation
- **AI-powered predictions** using RandomForestClassifier
- Input soil parameters (N, P, K, pH) and weather data
- Get top 3 crop recommendations with confidence scores
- Supports 22 different crop types

### 🧪 Fertilizer Recommendation
- Smart fertilizer calculations based on crop selection
- NPK deficiency analysis
- Specific fertilizer type recommendations
- Quantity calculations (kg/ha) for optimal growth

### 🌤️ Weather Integration
- Real-time weather data via OpenWeatherMap API
- 7-day weather forecasts
- Location-based insights
- Temperature, humidity, and condition displays

### 🤖 AI Chatbot Assistant
- **Powered by Google Gemini 1.5 Flash**
- Natural language farming advice
- Context-aware conversations
- Crop planning and fertilizer guidance
- Weather-based recommendations

### 🔐 User Authentication
- Role-based login (Farmer, Officer, User)
- Secure password hashing
- Session management
- User feedback system

### 📱 Modern UI/UX
- Responsive Bootstrap 5 design
- Mobile-friendly interface
- Floating chatbot widget
- Smooth animations and transitions
- Professional green-themed color palette

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- API keys (see setup below)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sridattasai18/Agri-Vision.git
   cd Agri-Vision
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

   Edit `.env` and add your API keys:
   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   OPENWEATHER_API_KEY="your_openweather_api_key_here"
   FLASK_SECRET_KEY="your_secret_key_here"
   FLASK_DEBUG="1"
   ```

### Getting API Keys

#### Google Gemini API Key (Required)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

**Free tier:** 60 requests/minute

#### OpenWeatherMap API Key (Required)
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to API keys section
4. Generate a new API key
5. Copy the key to your `.env` file

**Free tier:** 1,000 calls/day

#### Flask Secret Key (Required)
Generate a secure random key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output to your `.env` file

### Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

---

## 📖 Usage

### Demo Accounts
- **Farmer:** `farmer` / `farmer123`
- **Officer:** `officer` / `officer123`
- **Normal User:** `user` / `user123`

### Crop Recommendation Example

**Input:**
- Nitrogen (N): 90 ppm
- Phosphorus (P): 40 ppm
- Potassium (K): 40 ppm
- Temperature: 20.5°C
- Humidity: 80%
- pH: 6.5
- Rainfall: 200mm

**Output:**
```
Top Recommendations:
1. Rice (76.5% confidence)
2. Jute (23.0% confidence)
3. Coffee (0.5% confidence)
```

### Using the AI Chatbot

Click the floating chatbot button (bottom right) and ask questions like:
- "What crops should I plant this season?"
- "How do I improve soil fertility?"
- "What's the weather forecast for Mumbai?"
- "I need fertilizer advice for rice"

---

## 🏗️ Project Structure

```
AgriVision/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── src/
│   ├── backend/
│   │   ├── app.py                  # Flask application
│   │   ├── chatbot/
│   │   │   └── gemini_chatbot.py   # AI chatbot logic
│   │   └── utils/
│   │       └── weather_api.py      # Weather API integration
│   ├── frontend/
│   │   ├── templates/
│   │   │   ├── index.html          # Main page
│   │   │   ├── login.html          # Login page
│   │   │   └── signup.html         # Signup page
│   │   └── static/
│   │       ├── css/
│   │       │   ├── style.css       # Main styles
│   │       │   └── chatbot.css     # Chatbot widget styles
│   │       └── js/
│   │           ├── script.js       # Main JavaScript
│   │           ├── chatbot.js      # Chatbot widget
│   │           ├── login.js        # Login logic
│   │           └── signup.js       # Signup logic
│   ├── models/
│   │   ├── crop_model.joblib       # Trained ML model
│   │   └── features.json           # Model features
│   └── data/
│       ├── fertilizer.csv          # Fertilizer database
│       └── feedback.db             # SQLite database
└── tests/
    └── test_complete_workflow.py   # Integration tests
```

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main homepage |
| `/api/health` | GET | System health check |
| `/api/predict/crop` | POST | Get crop recommendations |
| `/api/predict/fertilizer` | POST | Get fertilizer suggestions |
| `/api/weather` | POST | Get current weather |
| `/api/weather/forecast` | POST | Get 7-day forecast |
| `/api/chatbot` | POST | AI chatbot interaction |
| `/api/login` | POST | User authentication |
| `/api/signup` | POST | User registration |
| `/api/logout` | POST | User logout |
| `/api/user` | GET | Get current user info |
| `/api/feedback` | POST | Submit feedback |

---

## 🧠 Machine Learning Model

- **Model Type:** RandomForestClassifier
- **Training Data:** Agricultural dataset with soil & weather parameters
- **Crop Classes:** 22 different crops
- **Input Features:** N, P, K, temperature, humidity, pH, rainfall
- **Accuracy:** ~90%+

### Supported Crops
rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

---

## 🧪 Testing

Run the complete workflow test:
```bash
python test_complete_workflow.py
```

This will test:
- File structure
- Server health
- Authentication flow
- ML model integration
- Weather API
- AI chatbot
- Disease detection placeholder

---

## 🚀 Deployment

AgriVision is production-ready and can be deployed on multiple platforms. See our **[Complete Deployment Guide](DEPLOYMENT.md)** for detailed instructions.

### Quick Deploy Options

#### Render.com (Recommended) ⭐
- **Free tier available**
- **One-click deploy from GitHub**
- **Automatic SSL certificates**

[Deploy to Render](https://render.com) | [Detailed Guide](DEPLOYMENT.md#option-1-rendercom-recommended-)

#### Railway.app
- **$5 free credit monthly**
- **Fast deployment**
- **Simple configuration**

[Deploy to Railway](https://railway.app) | [Detailed Guide](DEPLOYMENT.md#option-2-railwayapp)

#### Heroku
- **Industry standard**
- **Extensive add-ons**
- **Starts at $5/month**

[Deploy to Heroku](https://heroku.com) | [Detailed Guide](DEPLOYMENT.md#option-3-heroku)

### Environment Variables for Production

Set these in your deployment platform:

```env
GEMINI_API_KEY=your_actual_key
OPENWEATHER_API_KEY=your_actual_key
FLASK_SECRET_KEY=strong_random_key_here
FLASK_DEBUG=0
PORT=10000
```

### Deployment Files

The project includes:
- **`Procfile`** - Gunicorn configuration for web servers
- **`runtime.txt`** - Python 3.12.6 specification
- **`requirements.txt`** - Pinned dependencies
- **`DEPLOYMENT.md`** - Complete deployment guide

> [!IMPORTANT]
> **Large Model File:** The disease detection model (`plant_disease_model_1_latest.pt`, ~200MB) is **not included in the git repository** due to GitHub size limits. You must manually upload this file to `src/models/plant_disease/` on your server for disease detection to work.

### Health Check

After deployment, verify your app:
```bash
curl https://your-app-url.com/api/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "features_count": 7,
  "crop_classes": 22
}
```

### Common Issues

**Scikit-learn version warning:** This is expected and won't affect functionality. The model works across scikit-learn versions 1.5.x - 1.7.x.

**Gemini API deprecation:** The app uses `google-generativeai` which shows a deprecation warning but works perfectly. Migration to `google.genai` is planned for future updates.

**Model file size:** The disease detection model (`.pt` file) is ~200MB. Ensure your platform supports this file size.

For detailed troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md#-troubleshooting).

---

## 📈 Performance

- **Model Load:** ~2-3s on first startup
- **Prediction Time:** ~50-100ms per request
- **Memory Usage:** ~150-200MB typical
- **Supports:** Multiple concurrent users

---

## 🔒 Security Features

- CORS protection
- Input validation
- Graceful error handling
- Secure session management
- Password hashing (werkzeug)
- Environment variable validation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **scikit-learn** for machine learning
- **Flask** for web framework
- **Google Gemini** for AI capabilities
- **Bootstrap 5** for responsive UI
- **Font Awesome** for icons
- **OpenWeatherMap** for weather API

---

## 📞 Support

Having issues? Check these resources:
- Review the [setup instructions](#quick-start)
- Check the [API documentation](#api-endpoints)
- Test with the provided [demo accounts](#demo-accounts)
- Run the [test suite](#testing)

---

## 🎯 Roadmap

- [ ] Plant disease detection (CNN-based)
- [ ] Crop price tracking
- [ ] Government schemes integration
- [ ] Multi-language support (Hindi, Telugu)
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] PWA support

---

**Status:** ✅ Production Ready  
**Version:** 2.0.0  
**Last Updated:** January 2026

---

Made with ❤️ for farmers
