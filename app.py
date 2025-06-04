from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
# Fake story store (story_id, title, price)
STORIES = [
    {'id': 1, 'title': 'The AI Apocalypse', 'price': '$5'},
    {'id': 2, 'title': 'Love in the Machine Age', 'price': '$4'},
    {'id': 3, 'title': 'Escape from Data Valley', 'price': '$6'},
]

app.secret_key = 'your_secret_key_here'

# Connect to database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/buy.html', methods=['GET', 'POST'])
def buy_page():
    if 'username' not in session:
        return redirect('/account.html')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        story_id = int(request.form['story_id'])
        username = session['username']
        cursor.execute('INSERT INTO purchases (username, story_id) VALUES (?, ?)', (username, story_id))
        conn.commit()

    conn.close()
    return render_template('buy.html', stories=STORIES)


@app.route('/mystories.html')
def mystories_page():
    if 'username' not in session:
        return redirect('/account.html')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT story_id FROM purchases WHERE username = ?', (session['username'],))
    purchased_ids = [row['story_id'] for row in cursor.fetchall()]
    owned_stories = [story for story in STORIES if story['id'] in purchased_ids]

    conn.close()
    return render_template('mystories.html', username=session['username'], stories=owned_stories)


@app.route('/account.html', methods=['GET', 'POST'])
def account_page():
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()

        if action == 'signup':
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                message = 'Signup successful. Please log in.'
            except sqlite3.IntegrityError:
                message = 'Username already exists.'
        elif action == 'login':
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = username
                return redirect('/mystories.html')
            else:
                message = 'Invalid credentials.'

        conn.close()
    return render_template('account.html', message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
