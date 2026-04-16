# Research Guard 🛡️

A secure, AI-powered academic research repository that enables researchers to store, search, classify, and collaborate on confidential publication datasets — built as a Senior Design Capstone at NYIT.

![Research Guard Dashboard](assets/dashboard.png)

## Overview
Research Guard solves a critical problem: most research tools are built for public datasets, leaving confidential research poorly managed (often in Excel sheets with limited search and no collaboration). Research Guard provides a purpose-built platform with ML-powered classification, citation generation, and secure team collaboration.

## Key Features
- 🔍 **Smart Search** — search publications by title, abstract, URL, metadata, or category
- 🤖 **ML Classification** — train and run Naive Bayes, Logistic Regression, SVM, or Random Forest models on your dataset
- 📝 **Citation Generation** — instant citations in APA, MLA, and Chicago formats
- 🔗 **Shared Research Sessions** — collaborate with team members on curated publication sets
- 🔒 **Secure Access** — user authentication and session management via sanic-security
- 📋 **Research Memos** — annotate publications with notes for easy reference

## ML Model Performance (trained on 1.7M+ arXiv papers)
| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|----|
| Naive Bayes | 80.37% | 82.17% | 80.37% | 80.82% |
| Logistic Regression | 86.05% | 85.62% | 86.05% | 85.64% |
| **Linear SVM** | **86.12%** | **85.74%** | **86.12%** | **85.78%** |
| Random Forest | 52.96% | 80.20% | 52.96% | 57.56% |

## Tech Stack
**Backend**
- Python, Sanic (async web framework)
- Tortoise ORM (async ORM)
- PostgreSQL / SQLite
- sanic-security (authentication)

**Frontend**
- HTML, CSS, JavaScript
- Figma (design & wireframing)

**ML / NLP**
- Scikit-learn (Naive Bayes, Logistic Regression, SVM, Random Forest)
- TF-IDF Vectorization
- LabelEncoder, train_test_split

## Project Structure
```
research-guard/
│
├── research_guard/
│   ├── blueprints/
│   │   ├── ai/             # ML model training and inference
│   │   ├── research/       # Research session management
│   │   └── security/       # Authentication endpoints
│   ├── common/             # Shared utilities
│   └── models.py           # Tortoise ORM models
├── static/                 # Frontend assets (HTML/CSS/JS)
├── resources/              # Training data and saved models
├── server.py               # Sanic app entry point
└── README.md
```

## How to Run
```bash
# Clone the repository
git clone https://github.com/Vidhee843/research-guard.git
cd research-guard

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

## Screenshots
| Dashboard | Admin Panel | Citation Generator |
|-----------|-------------|-------------------|
| Search and manage publications | Train and deploy ML models | Generate APA/MLA/Chicago citations |

## Team
Nicholas Stewart, Jian Wang, **Vidhee Patel**, Tyler Williams

Senior Design Capstone — BS Computer Science, New York Institute of Technology (2024–2025).
