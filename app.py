from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    alert_text = data.get("text", "")

    result = subprocess.run(
        ["python", "auto.py"],
        input=alert_text,
        text=True,
        capture_output=True
    )

    return jsonify({
        "output": result.stdout
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
