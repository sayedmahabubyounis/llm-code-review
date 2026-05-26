from flask import Flask, render_template, request, jsonify
import os
import json
import urllib.request
import urllib.error
from datetime import datetime

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def call_gemini(prompt, temperature=0.3, max_tokens=3000):
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
          headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]

def clean_json(raw):
    raw = raw.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    return raw

# ── REVIEW ──
REVIEW_PROMPT = """You are an expert AI Code Reviewer. Analyze the code and respond ONLY with this exact JSON, no markdown, no extra text:
{{
  "summary": "2-3 sentence overall assessment",
  "score": <0-100>,
  "grade": "<A/B/C/D/F>",
  "issues": [
    {{
      "type": "<Bug|Security|Performance|Style>",
      "severity": "<Critical|High|Medium|Low>",
      "line": "<line number or range>",
      "title": "<short title>",
      "description": "<detailed explanation>",
      "fix": "<concrete fix with code>"
    }}
  ],
  "strengths": ["<strength>"],
  "refactored_snippet": "<improved version>",
  "metrics": {{"bugs": 0, "security": 0, "performance": 0, "style": 0}},
  "complexity": {{
    "cyclomatic": <1-20>,
    "maintainability": "<High|Medium|Low>",
    "lines_of_code": <count>,
    "comment_ratio": "<percentage>"
  }},
  "owasp": [
    {{
      "id": "<A01:2021 etc>",
      "name": "<OWASP name>",
      "detected": <true|false>,
      "description": "<what was found>"
    }}
  ]
}}"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/review", methods=["POST"])
def review_code():
    data = request.get_json()
    code = data.get("code", "").strip()
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "No code provided"}), 400
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not set"}), 500
    try:
        prompt = REVIEW_PROMPT + f"\n\nReview this {language} code:\n```{language}\n{code}\n```"
        raw = call_gemini(prompt)
        result = json.loads(clean_json(raw))
        result["language"] = language
        result["timestamp"] = datetime.now().strftime("%d %b %Y, %H:%M:%S")
        result["lines_reviewed"] = len(code.splitlines())
        result["original_code"] = code
        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({"error": "AI parsing failed. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── AUTO FIX ──
@app.route("/api/fix", methods=["POST"])
def fix_code():
    data = request.get_json()
    code = data.get("code", "").strip()
    language = data.get("language", "python")
    issues = data.get("issues", [])
    if not code:
        return jsonify({"error": "No code provided"}), 400
    try:
        issue_list = "\n".join([f"- {i.get('title','')}: {i.get('description','')}" for i in issues])
        prompt = f"""Fix ALL the following issues in this {language} code.
Issues to fix:
{issue_list}

Original code:
```{language}
{code}
```

Respond ONLY with JSON, no markdown:
{{
  "fixed_code": "<complete fixed code>",
  "changes": ["<change 1>", "<change 2>"],
  "explanation": "<brief summary of all fixes>"
}}"""
        raw = call_gemini(prompt, temperature=0.2, max_tokens=3000)
        result = json.loads(clean_json(raw))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── CHAT ──
@app.route("/api/chat", methods=["POST"])
def chat_code():
    data = request.get_json()
    code = data.get("code", "").strip()
    question = data.get("question", "").strip()
    language = data.get("language", "python")
    history = data.get("history", [])
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        history_text = ""
        for h in history[-4:]:
            history_text += f"User: {h['question']}\nAssistant: {h['answer']}\n\n"
        prompt = f"""You are an expert code assistant. Answer questions about the code clearly and concisely.

Code ({language}):
```{language}
{code}
```

{history_text}User: {question}
Assistant:"""
        answer = call_gemini(prompt, temperature=0.5, max_tokens=1000)
        return jsonify({"answer": answer.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status")
def status():
    return jsonify({"status": "running", "model": "gemini-1.5-flash",
                    "timestamp": datetime.utcnow().isoformat() + "Z"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
