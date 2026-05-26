from flask import Flask, render_template, request, jsonify
import os
import json
import urllib.request
import urllib.error
from datetime import datetime

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

SYSTEM_PROMPT = """You are an expert AI Code Reviewer. Analyze the given code and respond ONLY with this exact JSON format, no markdown, no extra text:
{
  "summary": "2-3 sentence overall assessment",
  "score": <integer 0-100>,
  "grade": "<A/B/C/D/F>",
  "issues": [
    {
      "type": "<Bug|Security|Performance|Style>",
      "severity": "<Critical|High|Medium|Low>",
      "line": "<line number or General>",
      "title": "<short title>",
      "description": "<detailed explanation>",
      "fix": "<concrete fix with code example>"
    }
  ],
  "strengths": ["<strength 1>", "<strength 2>"],
  "refactored_snippet": "<improved version of the most critical part>",
  "metrics": {
    "bugs": <count>,
    "security": <count>,
    "performance": <count>,
    "style": <count>
  }
}"""

def call_gemini(prompt):
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    payload = json.dumps({
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2000
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]

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
    if len(code) > 10000:
        return jsonify({"error": "Code too long. Max 10,000 characters."}), 400
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not set."}), 500

    try:
        prompt = f"Review this {language} code:\n\n```{language}\n{code}\n```"
        raw = call_gemini(prompt).strip()

        # Strip markdown fences if present
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)
        result["language"] = language
        result["timestamp"] = datetime.now().strftime("%d %b %Y, %H:%M:%S")
        result["lines_reviewed"] = len(code.splitlines())
        return jsonify(result)

    except json.JSONDecodeError:
        return jsonify({"error": "AI response parsing failed. Please try again."}), 500
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"Gemini API error: {e.code} {e.reason}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status")
def status():
    return jsonify({
        "status": "running",
        "model": "gemini-1.5-flash",
        "project": "LLM Code Review Assistant",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
