# Ai_Mood_Detector
This is a Flask-based web application that detects the user's mood in real-time using facial expressions. It uses a webcam, DeepFace for emotion detection, and stores mood data in a MySQL database.
# 😊 AI Mood Detector Web App

The **AI Mood Detector** is a full-stack web application that uses AI to detect human moods in real time using facial expressions. Built with a Flask backend and modern HTML/CSS/JS frontend, it allows users to register/login, analyze their mood using a webcam, and view their mood detection history.

---

## 💡 Project Features

- 🔐 User authentication (Register & Login)
- 📸 Real-time face capture using webcam
- 🤖 Mood detection using DeepFace & OpenCV
- 🧠 Optionally support custom-trained emotion model (`.h5`)
- 🗃️ MySQL database to store user details & mood history
- 🖥️ Clean frontend interface with multiple pages (Home, About, Contact, etc.)
- 📈 Mood detection history by date & time for each user

---

## 🛠️ Tech Stack

| Layer     | Technology                       |
|-----------|----------------------------------|
| Backend   | Python, Flask, DeepFace, OpenCV  |
| Frontend  | HTML, CSS, JavaScript            |
| Database  | MySQL, PyMySQL                   |
| ML Model  | DeepFace (or custom `.h5` model) |

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.x
- MySQL server installed
- Git (for cloning the repo)
- A working webcam
- A virtual environment (optional but recommended)

### 🔧 Installation

# 1. Clone the repository
git clone https://github.com/Sharsona27/AI_Mood_Detector.git
cd AI_Mood_Detector

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup your MySQL database
# (import db_setup.sql or create tables manually)

# 5. Run the app
python app.py
