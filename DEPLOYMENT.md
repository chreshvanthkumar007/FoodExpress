# FoodExpress Deployment Guide

This guide covers the best ways to deploy **FoodExpress** so that anyone in the world can access it over the public internet.

---

## ⚡ Option 1: Instant 1-Click Public Access (No Account Required)

If you need a live public HTTPS link right now (for evaluation, sharing with friends, or presentation):

1. Double-click `start_public.bat` (or select Option 2 in `start_foodexpress.bat`).
2. Cloudflare Tunnel will start and generate a free public link:
   ```text
   https://your-unique-subdomain.trycloudflare.com
   ```
3. Share that link with anyone — it connects securely directly to your running FoodExpress instance!

---

## ☁️ Option 2: Free 24/7 Cloud Hosting on Render (Recommended)

Render offers free cloud hosting for Flask web apps connected to GitHub.

### Step 1: Initialize Git and Push to GitHub
1. Open PowerShell or Command Prompt in `FoodExpress_Project`:
   ```powershell
   git init
   git add .
   git commit -m "Deploy FoodExpress ready for cloud"
   ```
2. Create a new repository on [GitHub](https://github.com/new) named `FoodExpress`.
3. Push your code:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/FoodExpress.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [dashboard.render.com](https://dashboard.render.com/) and sign up / log in with GitHub.
2. Click **New +** ➔ **Web Service**.
3. Select your `FoodExpress` GitHub repository.
4. Render will automatically detect the settings from `render.yaml` or you can enter:
   - **Name**: `foodexpress`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Under **Environment Variables**, add:
   - `USE_SQLITE` = `True` *(or provide your remote MySQL credentials)*
   - `SECRET_KEY` = *(click Generate or enter a random string)*
   - `PYTHON_VERSION` = `3.11.8`
6. Click **Create Web Service**.
7. In 2 minutes, your site will be live at:
   👉 `https://foodexpress-xxxx.onrender.com`

---

## 🚂 Option 3: Deploy on Railway

1. Go to [railway.app](https://railway.app/) and sign in with GitHub.
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Select your `FoodExpress` repository.
4. Add environment variables:
   - `USE_SQLITE` = `True` *(or add Railway's 1-click MySQL database plugin)*
   - `SECRET_KEY` = `foodexpress_super_secret_key_2026`
5. Railway will automatically build using the included `Dockerfile` or `Procfile` and assign you a free public domain!

---

## 🐍 Option 4: Deploy on PythonAnywhere

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com/).
2. Open a **Bash Console** in PythonAnywhere and clone your repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/FoodExpress.git
   ```
3. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 foodexpress-venv
   pip install -r requirements.txt
   ```
4. In the **Web** tab:
   - Create a **Manual Configuration (Flask)** app.
   - Set the virtualenv path to `~/.virtualenvs/foodexpress-venv`.
   - In the WSGI configuration file, point to `app.py`:
     ```python
     import sys
     path = '/home/YOUR_USERNAME/FoodExpress'
     if path not in sys.path:
         sys.path.append(path)
     from app import app as application
     ```
5. Click **Reload** — your app is live!

---

## 🐳 Option 5: Deploy with Docker (Self-Hosted VPS / AWS / DigitalOcean)

The project includes a production-ready `Dockerfile`:

```bash
# Build Docker image
docker build -t foodexpress .

# Run container on port 80
docker run -d -p 80:5000 --name foodexpress-app foodexpress
```
Navigate to `http://YOUR_SERVER_IP/`.
