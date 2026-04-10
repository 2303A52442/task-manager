# ✅ Task Manager

A modern, Dockerized Task Manager web application built with **Python Flask** and **Vanilla CSS**.

## Features

- ➕ Add tasks with title and optional description
- ✓ Mark tasks as done / undo completion
- 🗑 Delete tasks
- 📅 Timeline layout — dates on the left, task content on the right
- 🐳 Fully Dockerized for easy deployment
- 💜 Dark-mode glassmorphism UI

## Tech Stack

| Layer    | Technology          |
|----------|---------------------|
| Backend  | Python 3.11 + Flask |
| Frontend | HTML + Vanilla CSS  |
| Deploy   | Docker              |

## Getting Started

### Run Locally (without Docker)

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`

### Run with Docker

```bash
docker build -t task-manager .
docker run -p 5000:5000 task-manager
```

Visit `http://localhost:5000`

## Project Structure

```
task-manager/
├── app.py              # Flask backend (routes & logic)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image config
└── templates/
    └── index.html      # Frontend UI
```

## Output Screenshots

<img width="1825" height="851" alt="{0D27D428-E134-4EB1-B2BE-82F15E052789}" src="https://github.com/user-attachments/assets/e184c955-9343-430f-a46e-1e3af6dbe866" />


## License

MIT
