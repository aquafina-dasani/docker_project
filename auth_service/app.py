import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# users for demo
USERS = {
    "alice": "alice123",
    "bob": "bob123",
    "luis": "luis123",
    "nick": "nick123"
}

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.post("/validate")
def validate():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if username in USERS and USERS[username] == password:
        return jsonify(ok=True), 200
    else:
        return jsonify(ok=False, message="Invalid Credentials"), 401
    

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)