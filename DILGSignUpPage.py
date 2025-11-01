# DILGSignUpPage.py
from flask import render_template, request, redirect, url_for, session, flash
import sqlite3
import os

def dilg_signup():
    if request.method == 'POST':
        municipality = request.form.get('municipality')
        contact_no = request.form.get('contact_no')
        password = request.form.get('password')

        if not all([municipality, contact_no, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('dilg_signup_page'))

        db_path = os.path.join(os.path.dirname(__file__), 'database', 'dilg_cred.db')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dilg_users (
                    id INTEGER PRIMARY KEY,
                    municipality TEXT NOT NULL,
                    contact_no TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                INSERT INTO dilg_users (municipality, contact_no, password)
                VALUES (?, ?, ?)
            ''', (municipality, contact_no, password))
            conn.commit()
            conn.close()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('dilg_login_page'))
        except sqlite3.IntegrityError:
            flash('Contact number already registered.', 'error')
        except Exception as e:
            flash('Database error.', 'error')
            print(e)

    return render_template('DILGSignUpPage.html')