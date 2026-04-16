from datetime import datetime
import os
import secrets
import sqlite3
import uuid

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "task_manager.db"))


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
            """
        )


def get_payload_value(key: str) -> str:
    payload = request.get_json(silent=True) or request.form or {}
    value = payload.get(key, "")
    if isinstance(value, str):
        return value.strip()
    return value or ""


def require_authentication():
    username = session.get("username")
    if not username:
        return None, (jsonify({"message": "Authentication required."}), 401)
    return username, None


def user_tasks(username: str):
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, description, done, created_at
            FROM tasks
            WHERE username = ?
            ORDER BY created_at DESC, id DESC
            """,
            (username,),
        ).fetchall()

    return [task_response(row) for row in rows]


def task_response(task):
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "done": bool(task["done"]),
        "created_at": task["created_at"],
    }


@app.route("/api/me")
def me():
    username = session.get("username")
    return jsonify({"authenticated": bool(username), "username": username})


@app.route("/api/register", methods=["POST"])
def register():
    username = get_payload_value("username")
    password = get_payload_value("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    password_hash = generate_password_hash(password)

    try:
        with get_db_connection() as connection:
            connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists."}), 409

    return jsonify({"message": "Registration successful. Please log in."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    username = get_payload_value("username")
    password = get_payload_value("password")

    with get_db_connection() as connection:
        user = connection.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if user and check_password_hash(user["password_hash"], password):
        session["username"] = username
        return jsonify({"message": "Login successful.", "username": username})

    return jsonify({"message": "Invalid username or password."}), 401


@app.route("/api/logout", methods=["POST", "GET"])
def logout():
    session.pop("username", None)
    return jsonify({"message": "Logged out successfully."})


@app.route("/api/tasks", methods=["GET", "POST"])
def tasks_endpoint():
    username, error_response = require_authentication()
    if error_response:
        return error_response

    if request.method == "GET":
        return jsonify({"tasks": user_tasks(username)})

    title = get_payload_value("title")
    description = get_payload_value("description")

    if not title:
        return jsonify({"message": "Task title is required."}), 400

    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "done": 0,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "username": username,
    }

    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO tasks (id, title, description, done, created_at, username)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task["id"],
                task["title"],
                task["description"],
                task["done"],
                task["created_at"],
                task["username"],
            ),
        )

    return jsonify({"task": task_response(task)}), 201


@app.route("/api/tasks/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    username, error_response = require_authentication()
    if error_response:
        return error_response

    with get_db_connection() as connection:
        task = connection.execute(
            """
            SELECT id, title, description, done, created_at
            FROM tasks
            WHERE id = ? AND username = ?
            """,
            (task_id, username),
        ).fetchone()

        if task is None:
            return jsonify({"message": "Task not found."}), 404

        new_done = 0 if task["done"] else 1
        connection.execute(
            "UPDATE tasks SET done = ? WHERE id = ? AND username = ?",
            (new_done, task_id, username),
        )

    task_data = dict(task)
    task_data["done"] = new_done
    return jsonify({"task": task_response(task_data)})


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    username, error_response = require_authentication()
    if error_response:
        return error_response

    with get_db_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ? AND username = ?",
            (task_id, username),
        )

    if cursor.rowcount == 0:
        return jsonify({"message": "Task not found."}), 404

    return jsonify({"message": "Task deleted."})


def serves_frontend_asset(path: str) -> bool:
    return bool(path) and os.path.isfile(os.path.join(FRONTEND_DIST, path))


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    if path == "api" or path.startswith("api/"):
        return jsonify({"message": "Not found."}), 404

    if os.path.isdir(FRONTEND_DIST):
        if serves_frontend_asset(path):
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")

    return jsonify({"message": "React frontend build not found. Run the frontend build first."}), 500


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
