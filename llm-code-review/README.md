# 🤖 LLM-Powered Code Review Assistant

An AI-powered code review tool built with **Claude claude-sonnet-4**, Flask, and deployed on Render. Detects bugs, security vulnerabilities, performance issues, and suggests refactored code in real time.

> Built for AI Engineer Portfolio | by Sayed Mahabub Younis

---

## ✨ Features

- ✅ Real LLM review using Anthropic Claude claude-sonnet-4
- ✅ Detects Bugs, Security issues, Performance problems, Style issues
- ✅ Code scoring (0–100) with grade (A–F)
- ✅ Refactored code suggestions
- ✅ Supports Python, JavaScript, Java, C++, Go, SQL
- ✅ 3 sample code snippets to try instantly
- ✅ Auto-deploy via GitHub Actions → Render

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Anthropic Claude claude-sonnet-4 |
| Backend | Python 3, Flask |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Deployment | Render (free tier) |
| CI/CD | GitHub Actions |
| Version Control | Git, GitHub |

---

## 🚀 Local Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/llm-code-review.git
cd llm-code-review

# 2. Install
pip install -r requirements.txt

# 3. Set API key
cp .env.example .env
# Edit .env → add your Anthropic API key

# 4. Run
python app.py
# Visit http://localhost:5000
```

---

## ☁ Deploy to Render (Free & Real-Time)

### Step 1 — Get Anthropic API Key
👉 https://console.anthropic.com → API Keys → Create Key

### Step 2 — Push to GitHub
```bash
git init
git add .
git commit -m "feat: LLM code review assistant"
git remote add origin https://github.com/YOUR_USERNAME/llm-code-review.git
git push -u origin main
```

### Step 3 — Deploy on Render
1. Go to 👉 https://render.com → Sign up with GitHub
2. Click **New → Web Service**
3. Connect your `llm-code-review` repo
4. Fill in:
   - Name: `llm-code-review`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add Environment Variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: your API key
6. Click **Deploy** ✅

### Step 4 — Auto Deploy (GitHub Actions)
1. In Render → Settings → Copy **Deploy Hook URL**
2. GitHub repo → Settings → Secrets → Add:
   - Name: `RENDER_DEPLOY_HOOK`
   - Value: paste the URL

Now every `git push` auto-deploys! 🚀

---

## 📁 Project Structure

```
llm-code-review/
├── app.py                       # Flask app + Anthropic SDK
├── requirements.txt
├── Procfile                     # Render start command
├── .env.example
├── .gitignore
├── .github/workflows/
│   └── deploy.yml               # GitHub Actions CI/CD
├── templates/
│   └── index.html               # Full dashboard UI
└── README.md
```

---

## 📊 Resume Bullet

> Built an LLM-powered code review assistant using Anthropic Claude claude-sonnet-4 and Flask; designed a custom prompt engineering pipeline to classify bugs, security vulnerabilities, and anti-patterns with structured JSON output; deployed on Render with GitHub Actions CI/CD for automated delivery.
> **Tech Stack:** Python, Flask, Anthropic Claude API, HTML5, CSS3, JavaScript, Render, GitHub Actions.
