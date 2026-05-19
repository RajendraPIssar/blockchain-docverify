"""
routes/admin_routes.py
-----------------------
Admin-only endpoints for viewing all documents and platform stats.
"""

from flask import Blueprint, request, jsonify
from models.database import get_db
from routes.auth_routes import get_current_user

admin_bp = Blueprint("admin", __name__)


def require_admin():
    user = get_current_user()
    if not user:
        return None, (jsonify({"error": "Login required"}), 401)
    if user["role"] != "admin":
        return None, (jsonify({"error": "Admin access required"}), 403)
    return user, None


@admin_bp.route("/documents", methods=["GET"])
def all_documents():
    user, err = require_admin()
    if err:
        return err

    status_filter = request.args.get("status")
    db = get_db()
    if status_filter:
        docs = db.execute(
            "SELECT * FROM documents WHERE status = ? ORDER BY created_at DESC",
            (status_filter,),
        ).fetchall()
    else:
        docs = db.execute(
            "SELECT * FROM documents ORDER BY created_at DESC"
        ).fetchall()
    db.close()
    return jsonify([dict(d) for d in docs])


@admin_bp.route("/stats", methods=["GET"])
def stats():
    user, err = require_admin()
    if err:
        return err

    db = get_db()
    total    = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    verified = db.execute("SELECT COUNT(*) FROM documents WHERE status='verified'").fetchone()[0]
    flagged  = db.execute("SELECT COUNT(*) FROM documents WHERE status='flagged'").fetchone()[0]
    rejected = db.execute("SELECT COUNT(*) FROM documents WHERE status='rejected'").fetchone()[0]
    users    = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    verifs   = db.execute("SELECT COUNT(*) FROM verify_log").fetchone()[0]
    db.close()

    return jsonify({
        "total_documents":    total,
        "verified":           verified,
        "flagged":            flagged,
        "rejected":           rejected,
        "total_users":        users,
        "total_verifications": verifs,
    })


@admin_bp.route("/documents/<int:doc_id>/status", methods=["PATCH"])
def update_status(doc_id):
    user, err = require_admin()
    if err:
        return err

    new_status = request.args.get("status")
    if new_status not in ("verified", "flagged", "rejected", "pending"):
        return jsonify({"error": "Invalid status"}), 400

    db = get_db()
    db.execute("UPDATE documents SET status = ? WHERE id = ?", (new_status, doc_id))
    db.commit()
    db.close()
    return jsonify({"id": doc_id, "status": new_status})
