# app.py - Main Flask Application for Task Manager
# This file handles all backend logic and routes

from flask import Flask, render_template, request, redirect, url_for
import uuid  # Used to generate unique IDs for each task
from datetime import datetime  # Used to timestamp when a task is created

# Initialize the Flask application
app = Flask(__name__)

# In-memory storage for tasks (no database needed)
# Each task is a dictionary with: id, title, description, done status
tasks = []


# -----------------------------------------------
# ROUTE: Home - View all tasks
# -----------------------------------------------
@app.route('/')
def index():
    """Display all tasks on the home page."""
    return render_template('index.html', tasks=tasks)


# -----------------------------------------------
# ROUTE: Add a new task
# -----------------------------------------------
@app.route('/add', methods=['POST'])
def add_task():
    """Receive form data and add a new task to the list."""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    # Only add the task if a title was provided
    if title:
        task = {
            'id': str(uuid.uuid4()),   # Unique ID for each task
            'title': title,
            'description': description,
            'done': False,             # All tasks start as not done
            'created_at': datetime.now().strftime('%b %d, %Y')  # Human-readable date
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
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = not task['done']  # Flip the done status
            break
    return redirect(url_for('index'))


# -----------------------------------------------
# ROUTE: Delete a task
# -----------------------------------------------
@app.route('/delete/<task_id>')
def delete_task(task_id):
    """Remove a task from the list by its ID."""
    global tasks
    # Keep all tasks EXCEPT the one with the matching ID
    tasks = [task for task in tasks if task['id'] != task_id]
    return redirect(url_for('index'))


# -----------------------------------------------
# Run the application
# -----------------------------------------------
if __name__ == '__main__':
    # host='0.0.0.0' makes the app accessible from outside the container
    # debug=False is recommended for production/Docker use
    app.run(host='0.0.0.0', port=5000, debug=False)
