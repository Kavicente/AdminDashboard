# DILGLogInPage.py
from flask import render_template, request, redirect, url_for, session, flash
import sqlite3
import os

def get_dilg_users():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'dilg_cred.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT municipality, contact_no, password FROM dilg_users')
        users = cursor.fetchall()
        conn.close()
        return [dict(zip(['municipality', 'contact_no', 'password'], u)) for u in users]
    except:
        return []

def dilg_login():
    if request.method == 'POST':
        municipality = request.form.get('municipality')
        contact_no = request.form.get('contact_no')
        password = request.form.get('password')

        db_path = os.path.join(os.path.dirname(__file__), 'database', 'dilg_cred.db')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM dilg_users 
                WHERE municipality = ? AND contact_no = ? AND password = ?
            ''', (municipality, contact_no, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['dilg_user'] = {
                    'municipality': municipality,
                    'contact_no': contact_no
                }
                return redirect(url_for('dilg_dashboard'))
            else:
                flash('Invalid credentials.', 'error')
        except Exception as e:
            flash('Login error.', 'error')
            print(e)

    return render_template('DILGLogInPage.html', dilg_users=get_dilg_users())