from flask import Flask, request, jsonify
import subprocess
import sys
import os

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        alert_text = data.get("text", "")

        result = subprocess.run(
            [sys.executable, "auto.py"],  # 🔥 usa el python correcto
            input=alert_text,
            text=True,
            capture_output=True,
            env=os.environ.copy()  # 🔥 PASA VARIABLES DE ENTORNO
        )

        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
