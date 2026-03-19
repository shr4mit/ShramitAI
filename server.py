from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

API_KEY = os.getenv("OPENAI_API_KEY")

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.Text)
    reply = db.Column(db.Text)

# ================= LOGIN =================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "User exists"})

    hashed = generate_password_hash(data["password"])

    user = User(username=data["username"], password=hashed)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "registered"})

# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()

    if user and check_password_hash(user.password, data["password"]):
        login_user(user)
        return jsonify({"msg": "logged in"})

    return jsonify({"msg": "invalid"})

# ================= LOGOUT =================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "logged out"})

# ================= CHAT (WITH GUEST SUPPORT) =================

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "system", "content": "You are ShramitAI. Keep answers short."},
                    {"role": "user", "content": user_message}
                ]
            }
        )

        data = response.json()

        if "error" in data:
            return jsonify({"reply": data["error"]["message"]})

        reply = data["choices"][0]["message"]["content"]

        # Save ONLY if logged in
        if current_user.is_authenticated:
            chat = Chat(user_id=current_user.id, message=user_message, reply=reply)
            db.session.add(chat)
            db.session.commit()

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": str(e)})

# ================= HISTORY =================

@app.route("/history")
@login_required
def history():
    chats = Chat.query.filter_by(user_id=current_user.id).all()

    return jsonify([
        {"msg": c.message, "reply": c.reply}
        for c in chats
    ])
@app.route("/")
def home():
    return "ShramitAI Backend is Running 🚀"

# ================= RUN =================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

   if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=10000)