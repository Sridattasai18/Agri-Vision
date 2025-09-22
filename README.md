# 🌱 AgriVision - Smart Agriculture Platform

AgriVision is a **comprehensive AI-powered web application** designed for small and marginal farmers.
It provides **intelligent crop recommendations, smart fertilizer suggestions, real-time weather insights, and secure user authentication**, all in a modern responsive UI.

---

## 🚀 Features

### ✅ Crop Recommendation

* AI-powered predictions using **RandomForestClassifier**
* **Input:** Soil & weather parameters → (N, P, K, temperature, humidity, pH, rainfall)
* **Output:** Top 3 crop recommendations with probability scores
* Interactive crop selection for fertilizer recommendations

### ✅ Fertilizer Recommendation

* Smart fertilizer calculation based on crop selection
* NPK deficiency analysis
* Specific fertilizer type recommendations
* Quantity calculation (kg/ha) for optimal crop growth

### ✅ Weather Integration

* Real-time weather data via **OpenWeatherMap API**
* Location-based weather insights
* Temperature, humidity, and condition display
* Visual weather icons and information

### ✅ User Authentication

* Role-based login system (**Farmer, Officer, Normal User**)
* Secure password hashing (demo credentials provided)
* Session management

### ✅ Plant Disease Detection *(Coming Soon)*

* Placeholder API endpoint
* Roadmap for AI-based plant disease classification

### ✅ Modern UI/UX

* Responsive **Bootstrap 5** design
* Mobile-friendly interface
* Smooth animations and transitions
* Professional green-themed color palette

---

## 🏗️ Project Structure

```
AgriVision/
├── app.py                  # Flask backend server
├── requirements.txt        # Python dependencies
├── models/
│   ├── crop_model.joblib   # Trained ML model
│   └── features.json       # Model feature definitions
├── data/
│   └── fertilizer.csv      # Fertilizer database
├── templates/
│   └── index.html          # Main web interface
├── static/
│   ├── css/
│   │   └── style.css       # Custom styling
│   └── js/
│       └── script.js       # Frontend JavaScript
└── README.md               # Project documentation
```

---

## 🧠 Machine Learning Model

* **Model Type:** RandomForestClassifier
* **Training Data:** Agricultural dataset with soil & weather parameters
* **Crop Classes:** 22 different crops
* **Input Features:** N, P, K, temperature, humidity, pH, rainfall
* **Accuracy:** \~90%+ (high precision for crop recommendations)

### Supported Crops

`rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee`

---

## 🔧 API Endpoints

| Endpoint                  | Method | Description                           |
| ------------------------- | ------ | ------------------------------------- |
| `/`                       | GET    | Main homepage                         |
| `/api/health`             | GET    | System health check                   |
| `/api/predict/crop`       | POST   | Get crop recommendations              |
| `/api/predict/fertilizer` | POST   | Get fertilizer suggestions            |
| `/api/weather`            | POST   | Get weather data                      |
| `/api/predict/disease`    | POST   | Plant disease detection (Coming Soon) |
| `/api/login`              | POST   | User authentication                   |
| `/api/logout`             | POST   | User logout                           |
| `/api/user`               | GET    | Get current user info                 |

---

## 🚀 Quick Start

### Prerequisites

* Python **3.12+**
* pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd AgriVision

# Create virtual environment
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
OPENWEATHER_API_KEY="YOUR_OPENWEATHER_API_KEY"
FLASK_SECRET_KEY="a_strong_random_secret"
FLASK_DEBUG="1"
```

*(Note: `.env` is ignored by Git — never commit secrets.)*

### Run the Application

```bash
# Local development
python app.py

# Production (e.g. Render/Heroku)
gunicorn app:app
```

### Access

* Web app: [http://127.0.0.1:5000](http://127.0.0.1:5000)
* API health check: [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)

---

## 📱 Usage Guide

### User Login (Demo Accounts)

* **Farmer** → `farmer / farmer123`
* **Officer** → `officer / officer123`
* **Normal User** → `user / user123`

### Crop Recommendation Example

```bash
curl -X POST http://127.0.0.1:5000/api/predict/crop \
  -H "Content-Type: application/json" \
  -d '{"N":90,"P":40,"K":40,"temperature":20.5,"humidity":80,"ph":6.5,"rainfall":200}'
```

Expected Response:

```json
{
  "success": true,
  "predictions": [
    {"crop": "rice", "probability": 0.765},
    {"crop": "jute", "probability": 0.23},
    {"crop": "coffee", "probability": 0.005}
  ]
}
```

---

## 🎨 UI Features

* Responsive design (desktop, tablet, mobile)
* Green agricultural theme
* Smooth transitions, hover effects, fade-ins
* Font Awesome icons for visual appeal

---

## 🔒 Security Features

* CORS protection
* Input validation
* Graceful error handling
* Secure session management
* Password hashing for users

---

## 📈 Performance

* Model Load: \~2-3s on first startup
* Prediction Time: \~50-100ms per request
* Memory Usage: \~150-200MB typical
* Supports multiple concurrent users

---

## 🚀 Deployment

AgriVision is production-ready and can be deployed on:

* **Render.com**
* **Railway.app**
* **Google Cloud Run**
* **Heroku**
* **AWS EC2**

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes and test thoroughly
4. Submit a Pull Request

---

## 📄 License

This project is open source and available under the **MIT License**.

---

## 🙏 Acknowledgments

* **Scikit-learn** for ML
* **Flask** for web framework
* **Bootstrap** for responsive UI
* **Font Awesome** for icons
* **OpenWeatherMap** for weather API

---

## 📞 Support

* Check troubleshooting section
* Review API docs
* Test with provided sample data
* Open an issue on GitHub

---

**Status:** ✅ Production Ready
**Version:** 1.0.0
**Last Updated:** September 2024

---

✨ Live Demo (local): [http://127.0.0.1:5000](http://127.0.0.1:5000)

---
