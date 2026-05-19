"""
DocVerify Chain - Backend API
Group Project: Blockchain Document Verification System
Masters in Computer Science - Group 4

Members:
  - Authentication & Database (auth_routes.py)
  - Document Upload & Hashing (document_routes.py)
  - Blockchain Integration (blockchain_service.py)
  - AI Fraud Detection (fraud_service.py)
"""

import os
from flask import Flask, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from models.database import init_db
from routes.auth_routes import auth_bp
from routes.document_routes import doc_bp
from routes.admin_routes import admin_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "docverify-secret-2024")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

# Allow all origins so the app works whether opened from file:// or a web server
CORS(app, origins="*", allow_headers=["Authorization", "Content-Type", "Accept"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

# Register route blueprints
app.register_blueprint(auth_bp,  url_prefix="/api/auth")
app.register_blueprint(doc_bp,   url_prefix="/api/docs")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

# Create all SQLite tables on startup
with app.app_context():
    init_db()


@app.route("/")
def index():
    """Serve the frontend so the app runs entirely on http://127.0.0.1:5000"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return send_file(os.path.abspath(frontend_path))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
