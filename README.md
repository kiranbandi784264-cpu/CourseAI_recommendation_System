# ⚡ CourseAI — Intelligent Course Recommendation & Job Skill Gap Engine

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.2%2B-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**CourseAI** is a full-stack AI-driven course recommendation platform and career pathway engine. It integrates **8 distinct machine learning & deep learning recommendation models**, an interactive **AI Study Assistant bot**, job skill gap radar visualizations, week-by-week syllabi, and reference literature recommendations.

---

## 🌟 Key Features

### 1. 🧠 8 AI Recommendation Models
- **Hybrid Fusion (Best Performer — Precision@10: 0.8520)**: Weighted ensemble of collaborative filtering, content similarity, and job-market demand vectors.
- **LightGCN (Graph Neural Network)**: High-order user-item graph connectivity learning for sparse collaborative ranking.
- **Neural Collaborative Filtering (NCF)**: Non-linear dual-embedding deep neural network with PyTorch.
- **Job-Skill Gap Matching**: Real-time vector gap matching between learner competencies and targeted industry roles.
- **User-Based Collaborative Filtering**: Pearson cosine similarity across user interaction profiles.
- **Item-Based Collaborative Filtering**: Item co-enrollment and rating patterns.
- **Content-Based Filtering**: TF-IDF vectorization across course titles, descriptions, and syllabi.
- **Implicit Feedback Matrix Factorization**: Alternating least squares (ALS) on implicit interaction signals.

---

### 2. 🤖 AI Study Assistant & Tutor
- Integrated directly in the top sticky navigation bar for instant access without scrolling.
- Provides immediate answers on course prerequisites, syllabi breakdowns, and custom learning roadmaps.
- Includes one-click quick prompt chips for common career queries.

---

### 3. 📚 Syllabi & Curated Reference Textbooks
- Detailed 4-week modular breakdown for each recommended course.
- Hand-curated academic textbooks and reference literature with author details and direct search/purchase links.

---

### 4. 📊 Analytics & Visualizations
- **Skill Gap Radar Chart**: Visualizes current competencies vs. targeted industry job profiles.
- **Precision@10 Model Benchmark**: Real-time horizontal bar comparison across all 8 recommendation algorithms.
- **Course Comparator**: Side-by-side comparative analysis of syllabus, difficulty level, duration, and ratings.

---

### 5. ✨ Rich Interactive Design & Animations
- Star particle dynamic canvas with comet streaks.
- 3D perspective tilt on stats cards and magnetic cursor tracking.
- Ripple click feedback on interactive buttons.

---

### 6. 🖥️ Interactive Presentation Deck
- Standalone 10-slide interactive presentation (`CourseAI_Interactive_Presentation.html` and `/presentation` route).
- Animated slide transitions, keyboard navigation (`←`/`→`/`F`), and integrated live benchmarks.

---

## 📁 Repository Structure

```
Course-Recommendation-System/
├── app.py                               # Flask application backend & API endpoints
├── run_pipeline.py                      # Training & score generation pipeline
├── start_courseai.bat                   # 1-Click Windows launcher script
├── requirements.txt                     # Clean project dependencies
├── CourseAI_Interactive_Presentation.html # Standalone interactive presentation deck
├── data/                                # Dataset & precomputed score matrices
│   ├── cleaned/                         # Cleaned user, course, and job datasets
│   └── score_matrices/                  # Computed recommendation score matrices
├── figures/                             # Visualizations, EDA charts, and figures
├── src/                                 # Machine learning source modules
│   ├── hybrid_recommender.py
│   ├── lightgcn_model.py
│   ├── ncf_model.py
│   ├── content_based.py
│   ├── collaborative_filtering.py
│   └── skill_gap_matcher.py
├── static/                              # Static media assets, clipart, presentation
│   ├── book_clipart.jpg
│   └── presentation.html
└── templates/
    └── index.html                       # Responsive frontend single-page application
```

---

## 🚀 Quick Start Guide

### Option A: One-Click Launch (Windows)
Double-click `start_courseai.bat`. It will automatically verify Python, install dependencies, and launch the web server.

### Option B: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Course-Recommendation-System.git
   cd Course-Recommendation-System
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Re-train all 8 recommendation models:**
   ```bash
   python run_pipeline.py
   ```

5. **Start the Flask web server:**
   ```bash
   python app.py
   ```

6. **Open in browser:**
   - **Main Web Application:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - **Interactive Presentation Deck:** [http://127.0.0.1:5000/presentation](http://127.0.0.1:5000/presentation)

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Main single-page interactive application |
| `/presentation` | `GET` | 10-Slide interactive presentation deck |
| `/download-presentation` | `GET` | 1-Click download for offline presentation deck |
| `/api/recommend` | `GET` | Fetch top-K recommendations by `user`, `job`, and `model` |
| `/api/stats` | `GET` | Retrieve dataset metrics (total courses, users, jobs) |
| `/api/chat` | `POST` | AI Study Tutor prompt assistant |
| `/api/run-pipeline` | `POST` | Trigger pipeline retraining across all 8 models |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.9+, Flask 3.0, PyTorch, Scikit-Learn, Pandas, NumPy, SciPy
- **Frontend:** HTML5, Modern CSS (Glassmorphism, CSS Grid, Flexbox), Vanilla JS, Chart.js
- **Animations:** HTML5 2D Canvas Particle Engine, CSS 3D Transforms, Web Animations API

---

## 📄 License
This project is licensed under the MIT License — see the LICENSE file for details.
