# 🚀 AgriVision Deployment Guide

Complete guide for deploying AgriVision to various cloud platforms.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] Created accounts on your chosen platform
- [x] Obtained API keys:
  - Google Gemini API key
  - OpenWeatherMap API key
- [x] Generated a secure Flask secret key
- [x] Reviewed the code and tested locally

---

## 🌐 Deployment Options

### Option 1: Render.com (Recommended) ⭐

**Why Render?**
- Free tier available
- Automatic deployments from GitHub
- Easy environment variable management
- Built-in SSL certificates

**Steps:**

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/Agri-Vision.git
   git push -u origin main
   ```

2. **Create New Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `agrivision`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

3. **Set Environment Variables**
   In the Render dashboard, add:
   ```
   GEMINI_API_KEY=your_actual_gemini_key
   OPENWEATHER_API_KEY=your_actual_openweather_key
   FLASK_SECRET_KEY=your_generated_secret_key
   FLASK_DEBUG=0
   PORT=10000
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your app will be live at `https://agrivision.onrender.com`

**Free Tier Limitations:**
- App spins down after 15 minutes of inactivity
- 750 hours/month free
- Slower cold starts

---

### Option 2: Railway.app

**Why Railway?**
- Simple deployment process
- $5 free credit monthly
- Fast build times

**Steps:**

1. **Install Railway CLI** (optional)
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy via GitHub**
   - Go to [Railway](https://railway.app/)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and uses Procfile

3. **Add Environment Variables**
   In Railway dashboard → Variables:
   ```
   GEMINI_API_KEY=your_key
   OPENWEATHER_API_KEY=your_key
   FLASK_SECRET_KEY=your_key
   FLASK_DEBUG=0
   ```

4. **Generate Domain**
   - Go to Settings → Generate Domain
   - Your app will be live at `https://agrivision.up.railway.app`

---

### Option 3: Heroku

**Why Heroku?**
- Industry standard
- Extensive documentation
- Many add-ons available

**Steps:**

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create agrivision-app
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set OPENWEATHER_API_KEY=your_key
   heroku config:set FLASK_SECRET_KEY=your_key
   heroku config:set FLASK_DEBUG=0
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Open App**
   ```bash
   heroku open
   ```

**Note:** Heroku no longer offers free tier. Starts at $5/month.

---

### Option 4: Google Cloud Run

**Why Cloud Run?**
- Serverless (pay per use)
- Scales to zero
- Google Cloud integration

**Steps:**

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD exec gunicorn --bind :$PORT --workers 2 --timeout 120 app:app
   ```

2. **Build and Deploy**
   ```bash
   gcloud run deploy agrivision \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Set Environment Variables**
   ```bash
   gcloud run services update agrivision \
     --set-env-vars GEMINI_API_KEY=your_key,OPENWEATHER_API_KEY=your_key,FLASK_SECRET_KEY=your_key,FLASK_DEBUG=0
   ```

---

## 🔧 Post-Deployment Configuration

### Database Setup

The SQLite database will be created automatically on first run. For production, consider:

**Option A: Keep SQLite (Simple)**
- Works for small to medium traffic
- No additional setup needed
- Data persists on platform's disk

**Option B: Migrate to PostgreSQL (Recommended for Production)**
- Better for concurrent users
- More reliable for production
- Available on most platforms

### File Uploads

For disease detection image uploads:
- **Development:** Local filesystem (default)
- **Production:** Consider cloud storage (AWS S3, Google Cloud Storage)

---

## 🐛 Troubleshooting

### Issue: App crashes on startup

**Solution:**
```bash
# Check logs
render logs  # Render
railway logs # Railway
heroku logs --tail # Heroku

# Common causes:
# 1. Missing environment variables
# 2. Wrong Python version
# 3. Dependency conflicts
```

### Issue: "Model file not found" error

**Solution:**
- The disease detection model (`.pt` file) is excluded from git due to GitHub's file size limit (>100MB).
- **For Deployment:** You must upload `src/models/plant_disease/plant_disease_model_1_latest.pt` manually to your server or use a cloud storage link to download it during build.
- **Local Development:** The file should already be in your local directory.

### Issue: Scikit-learn version warning

**Solution:**
This is a warning, not an error. The app will work fine. To fix:
```bash
# Retrain model with current scikit-learn version
# Or suppress warning in code (already handled)
```

### Issue: Gemini API deprecation warning

**Solution:**
This is a FutureWarning. The app works fine. To migrate:
```bash
pip install google-genai
# Update imports in gemini_chatbot.py
```

---

## 📊 Monitoring & Maintenance

### Health Check Endpoint

Test your deployment:
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

### Performance Tips

1. **Enable Caching**
   - Cache weather API responses (5-10 minutes)
   - Cache crop predictions for identical inputs

2. **Optimize Model Loading**
   - Models load once at startup
   - Use gunicorn with 2-4 workers

3. **Monitor API Usage**
   - Gemini: 60 requests/minute (free tier)
   - OpenWeather: 1,000 calls/day (free tier)

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Verify it's in .gitignore
   git check-ignore .env
   ```

2. **Use strong secret keys**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Set FLASK_DEBUG=0 in production**

4. **Regularly update dependencies**
   ```bash
   pip list --outdated
   ```

---

## 📈 Scaling Considerations

### For High Traffic:

1. **Increase Workers**
   ```
   # In Procfile
   web: gunicorn --workers 4 --timeout 120 app:app
   ```

2. **Add Redis Caching**
   ```bash
   pip install redis flask-caching
   ```

3. **Use CDN for Static Files**
   - CloudFlare
   - AWS CloudFront

4. **Database Migration**
   - Move from SQLite to PostgreSQL
   - Use connection pooling

---

## 🎯 Quick Deploy Commands

**Render (via CLI):**
```bash
# Install Render CLI
npm install -g @render/cli

# Deploy
render deploy
```

**Railway:**
```bash
railway up
```

**Heroku:**
```bash
git push heroku main
```

---

## 📞 Support

If you encounter issues:

1. Check platform-specific logs
2. Review environment variables
3. Verify API keys are valid
4. Test locally first: `python app.py`
5. Check GitHub Issues for similar problems

---

**Happy Deploying! 🚀**

For more help, see the [main README](README.md) or create an issue on GitHub.
