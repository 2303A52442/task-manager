# Task Manager

This project now uses a React frontend with a Flask JSON API and an SQLite database. The old Jinja templates are no longer part of the runtime path; Flask now handles authentication, database-backed task storage, and API responses, while React renders the UI.

## Stack

* React + Vite frontend
* Flask backend API
* SQLite database for users and tasks
* Docker multi-stage build

## Features

* Register and log in
* Create, complete, and delete tasks
* Session-based access control
* Responsive React dashboard

## Project Structure

```
task-manager/
├── app.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   └── vite.config.js
├── requirements.txt
├── Dockerfile
└── README.md
```

## Local Development

Install the Python backend dependency and the frontend packages.

```bash
pip install -r requirements.txt
cd frontend
npm install
```

Run the Flask API in one terminal.

```bash
python app.py
```

Run the React dev server in another terminal.

```bash
cd frontend
npm run dev
```

The Vite dev server proxies API calls to `http://127.0.0.1:5000`.

## Production Docker Build

```bash
docker build -t task-manager .
docker run -p 5000:5000 task-manager
```

## API Endpoints

* `GET /api/me`
* `POST /api/register`
* `POST /api/login`
* `POST /api/logout`
* `GET /api/tasks`
* `POST /api/tasks`
* `POST /api/tasks/<task_id>/toggle`
* `DELETE /api/tasks/<task_id>`

## Notes

* Task and user data are stored in SQLite, so restarting the server keeps them as long as the database file remains.
* The React app is served from the Flask process in production after the frontend build completes.
