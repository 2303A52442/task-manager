# ✅ Task Manager (DevOps + Full Stack Project)

## 📌 Overview

This project is a web-based Task Manager application built using Flask. It allows users to create, update, and manage tasks efficiently. The application is containerized using Docker and deployed on a cloud platform (Render), demonstrating core DevOps practices.

---

## 🚀 Live Demo

👉 https://task-manager-bdr7.onrender.com

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS (Jinja Templates)
* **Containerization:** Docker
* **Deployment:** Render
* **Version Control:** GitHub

---

## ✨ Features

* Create new tasks
* View all tasks
* Update existing tasks
* Delete tasks
* Simple and clean UI
* Deployed using Docker container

---

## 🧱 Project Structure

```
task-manager/
│── templates/        # HTML templates
│── app.py            # Main Flask application
│── requirements.txt  # Dependencies
│── Dockerfile        # Container configuration
│── README.md         # Project documentation
```

---

## ⚙️ How It Works (Architecture)

```
User → Browser → Flask Application → Docker Container → Render Deployment
```

* User interacts via browser
* Flask handles backend logic
* Docker packages the application
* Render hosts and runs the container

---

## 🐳 Docker Setup

To run the project using Docker:

```bash
docker build -t task-manager .
docker run -p 5000:5000 task-manager
```

---

## 💻 Local Setup

1. Clone the repository:

```bash
git clone https://github.com/2303A52442/task-manager.git
cd task-manager
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open in browser:

```
http://127.0.0.1:5000
```

---

## 🔄 DevOps Practices Implemented

* Containerization using Docker
* Cloud deployment using Render
* Version control with GitHub
* Basic project structuring

---

## ⚠️ Limitations

* No user authentication
* Uses basic UI (template-based)
* Limited scalability

---

## 🚀 Future Enhancements

* Add user authentication (login/signup)
* Integrate database (PostgreSQL/MySQL)
* Implement REST APIs
* Add CI/CD pipeline (GitHub Actions)
* Improve UI with React or modern frameworks


---

## 📎 Repository Link

👉 https://github.com/2303A52442/task-manager

---

