# app.py - Main Flask Application for Task Manager
# This file handles all backend logic and routes

from flask import Flask, render_template, request, redirect, url_for, session, flash
import uuid  # Used to generate unique IDs for each task
from datetime import datetime  # Used to timestamp when a task is created
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage for tasks and users (no database needed)
# Each task is a dictionary with: id, title, description, done status, username
tasks = []
users = {}  # Maps username -> hashed_password


# -----------------------------------------------
# ROUTE: Register
# -----------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for('register'))
            
        if username in users:
            flash("Username already exists.")
            return redirect(url_for('register'))
            
        users[username] = generate_password_hash(password)
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
        
    return render_template('register.html')

# -----------------------------------------------
# ROUTE: Login
# -----------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('index'))
            
        flash("Invalid username or password.")
        return redirect(url_for('login'))
        
    return render_template('login.html')

# -----------------------------------------------
# ROUTE: Logout
# -----------------------------------------------
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# -----------------------------------------------
# ROUTE: Home - View all tasks
# -----------------------------------------------
@app.route('/')
def index():
    """Display all tasks on the home page."""
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user_tasks = [t for t in tasks if t.get('username') == session['username']]
    return render_template('index.html', tasks=user_tasks, username=session['username'])


# -----------------------------------------------
# ROUTE: Add a new task
# -----------------------------------------------
@app.route('/add', methods=['POST'])
def add_task():
    """Receive form data and add a new task to the list."""
    if 'username' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    # Only add the task if a title was provided
    if title:
        task = {
            'id': str(uuid.uuid4()),   # Unique ID for each task
            'title': title,
            'description': description,
            'done': False,             # All tasks start as not done
            'created_at': datetime.now().strftime('%b %d, %Y'),  # Human-readable date
            'username': session['username']
        }
        tasks.append(task)

    # Redirect back to the home page after adding
    return redirect(url_for('index'))


# -----------------------------------------------
# ROUTE: Toggle task completion
# -----------------------------------------------
@app.route('/toggle/<task_id>')
def toggle_task(task_id):
    """Mark a task as done or not done."""
    if 'username' not in session:
        return redirect(url_for('login'))

    for task in tasks:
        if task['id'] == task_id and task.get('username') == session['username']:
            task['done'] = not task['done']  # Flip the done status
            break
    return redirect(url_for('index'))


# -----------------------------------------------
# ROUTE: Delete a task
# -----------------------------------------------
@app.route('/delete/<task_id>')
def delete_task(task_id):
    """Remove a task from the list by its ID."""
    if 'username' not in session:
        return redirect(url_for('login'))

    global tasks
    # Keep all tasks EXCEPT the one with the matching ID for this user
    tasks = [task for task in tasks if not (task['id'] == task_id and task.get('username') == session['username'])]
    return redirect(url_for('index'))


# -----------------------------------------------
# Run the application
# -----------------------------------------------
if __name__ == '__main__':
    # host='0.0.0.0' makes the app accessible from outside the container
    # debug=False is recommended for production/Docker use
    app.run(host='0.0.0.0', port=5000, debug=False)
