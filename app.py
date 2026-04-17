from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ DATABASE SETUP (AUTO FIXES OLD DB)
def init_db():
    conn = sqlite3.connect('database.db')

    # create table if not exists (without time first)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            message TEXT
        )
    ''')

    # 🔥 add time column if not exists
    try:
        conn.execute('ALTER TABLE feedback ADD COLUMN time TEXT')
    except:
        pass

    conn.close()

init_db()


# 🔐 LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/home')
        else:
            return render_template('login.html', error="Invalid login")

    return render_template('login.html')


# 🏠 HOME PAGE (FORM)
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name']
        feedback = request.form['feedback']

        # ⏰ time
        time = datetime.now().strftime("%d %b %Y, %I:%M %p")

        conn = sqlite3.connect('database.db')
        conn.execute(
            'INSERT INTO feedback (name, message, time) VALUES (?, ?, ?)',
            (name, feedback, time)
        )
        conn.commit()
        conn.close()

        return render_template('index.html', success=True)

    return render_template('index.html')


# 📋 VIEW FEEDBACK
@app.route('/feedbacks')
def feedbacks():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    data = conn.execute('SELECT * FROM feedback').fetchall()
    conn.close()

    return render_template('feedbacks.html', data=data)


# 🗑️ DELETE
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM feedback WHERE id=?', (id,))
    conn.commit()
    conn.close()

    return redirect('/feedbacks')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
