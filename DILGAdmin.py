# DILGAdmin.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
import ast
import requests
import sqlite3
import os
from DILGDashboard import get_dilg_dashboard_data
from DILGSignUpPage import dilg_signup
from DILGLogInPage import dilg_login

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBSXRZPDX1x1d91Ck-pskiwGA8Y2-5gDVs')
barangay_coords = {}
try:
    with open(os.path.join(os.path.dirname(__file__), 'assets', 'coords.txt'), 'r') as f:
        barangay_coords = ast.literal_eval(f.read())
except FileNotFoundError:
    logger.error("coords.txt not found in assets directory. Using empty dict.")
except Exception as e:
    logger.error(f"Error loading coords.txt: {e}. Using empty dict.")
    
municipality_coords = {
    "San Pablo City": {"lat": 14.0642, "lon": 121.3233},
    "Quezon Province": {"lat": 13.9347, "lon": 121.9473},
}




app = Flask(__name__)
app.secret_key = 'dilg_secret_key_2025'
socketio = SocketIO(app)

# DATABASE URL
ALERTNOW_DB_URL = "https://alertnow-wi0n.onrender.com"

# ROUTES
@app.route('/')
def home():
    return redirect(url_for('dilg_signup_page'))

@app.route('/dilg_login', methods=['GET', 'POST'])
def dilg_login_page():
    return dilg_login()

@app.route('/dilg_signup', methods=['GET', 'POST'])
def dilg_signup_page():
    return dilg_signup()

@app.route('/dilg_dashboard')
def dilg_dashboard():
    if 'dilg_user' not in session:
        return redirect(url_for('dilg_login_page'))
    data = get_dilg_dashboard_data()
    return render_template(
        'DILGDashboard.html',
        data=data,
        stats=data['stats'],
        responded_count=data['responded_count'],
        pending_count=data['pending_count'],
        **session['dilg_user']
    )

@app.route('/logout')
def logout():
    session.pop('dilg_user', None)
    return redirect(url_for('dilg_login_page'))

if __name__ == '__main__':
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'dilg_cred.db')
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                contact_no TEXT UNIQUE NOT NULL,
                assigned_municipality TEXT,
                province TEXT,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database 'users_web.db' initialized successfully or already exists.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)