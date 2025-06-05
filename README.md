# 🧠 AutoBrief – Intelligent News Summarizer with Bias Detection

AutoBrief is a Flask-based web application that helps users analyze news articles using AI.  
It summarizes lengthy articles and detects potential bias using NLP techniques.

---

## 🚀 Features

- 🔍 **News Summarization** (Abstractive + Extractive using BART/T5)
- 🧭 **Bias Detection** (via sentiment & subjectivity analysis using TextBlob/VADER)
- 🌐 **Multilingual Support** (English, Hindi, Malayalam, Tamil)
- 🎨 **Clean UI** (HTML, CSS, Gen-Z friendly design)

---

## 🛠️ Tech Stack

| Category       | Tech Used |
|----------------|-----------|
| Frontend       | HTML, CSS, JS |
| Backend        | Flask |
| NLP Libraries  | HuggingFace Transformers (BART, T5), NLTK, SpaCy |
| Bias Detection | TextBlob, VADER |
| Database       | SQLite / MongoDB (optional) |
| Deployment     | GitHub (code), Render (live preview) |

---

## 📂 Folder Structure
AutoBrief/
├── app.py                
├── requirements.txt       
├── templates/             
│   └── index.html
├── .venv/                 
├── .gitignore            
└── README.md              


## 💡 How It Works

1. Paste a news article or URL
2. App extracts and summarizes key points
3. It analyzes the sentiment and detects bias
4. You get a concise summary and a bias report 🔥

## 📦 Installation (Local Setup)

```bash
git clone https://github.com/Sree051203/AutoBrief.git
cd AutoBrief/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py

Then open your browser at http://127.0.0.1:5000

🌐 Live Demo-Coming Soon on Render / Replit!

✨ Author
Sreelakshmi M
🚀 ML + AI Developer | Founder @ spydX(https://thespydx.com)
📫 LinkedIn | GitHub 

📜 License
## ✅ Final Step

1. Copy this README into your `README.md` on GitHub or VS Code
2. Commit & push:
```bash
git add README.md
git commit -m "Added detailed README for AutoBrief"
git push

