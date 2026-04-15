from flask import Flask, request, jsonify
import subprocess
import sys
import os
import json

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        alert_text = data.get("text", "")

        if not alert_text:
            return jsonify({
                "success": False,
                "error": "No text provided"
            }), 400

        # 🔥 Ejecutar script correctamente en cualquier entorno (Render incluido)
        result = subprocess.run(
            [sys.executable, "auto.py"],  # 🔥 clave
            input=alert_text,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=os.environ  # 🔥 clave
        )

        # 🔴 Si el script falla
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }), 500

        # 🧠 Intentar parsear JSON del auto.py
        try:
            parsed_output = json.loads(result.stdout)
            return jsonify(parsed_output)
        except:
            # fallback si no es JSON
            return jsonify({
                "success": True,
                "raw_output": result.stdout
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
