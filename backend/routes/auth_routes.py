"""
routes/auth_routes.py
---------------------
Handles user registration, login, and JWT token creation.
No external auth library — we use PyJWT directly.
"""

from flask import Blueprint, request, jsonify
from models.database import get_db
import hashlib, jwt, datetime, os

auth_bp = Blueprint("auth", __name__)
# Must be at least 32 bytes for HMAC-SHA256 (PyJWT 2.9+ enforces this)
SECRET = os.getenv("SECRET_KEY", "docverify-chain-secret-key-2024-group4")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def make_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "sub":   str(user_id),   # PyJWT 2.9+ requires sub to be a string
        "email": email,
        "role":  role,
        "exp":   datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=["HS256"])


def get_current_user():
    """Extract user from Authorization header. Returns user dict or None."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        data = decode_token(token)
        user_id = int(data["sub"])   # sub was stored as string, convert back to int
        db   = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        db.close()
        return dict(user) if user else None
    except Exception:
        return None


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    body = request.get_json()
    email     = body.get("email", "").strip().lower()
    password  = body.get("password", "")
    full_name = body.get("full_name", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({"error": "Email already registered"}), 409

    db.execute(
        "INSERT INTO users (email, password, full_name) VALUES (?, ?, ?)",
        (email, hash_password(password), full_name),
    )
    db.commit()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    token = make_token(user["id"], user["email"], user["role"])
    return jsonify({"token": token, "email": email, "role": user["role"]}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body     = request.get_json()
    email    = body.get("email", "").strip().lower()
    password = body.get("password", "")

    db   = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = make_token(user["id"], user["email"], user["role"])
    return jsonify({
        "token":     token,
        "email":     user["email"],
        "full_name": user["full_name"],
        "role":      user["role"],
    })


@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "id":        user["id"],
        "email":     user["email"],
        "full_name": user["full_name"],
        "role":      user["role"],
    })
