"""
routes/document_routes.py
--------------------------
Upload a document → hash it → run fraud check → register on blockchain.
Verify endpoint checks blockchain first, falls back to database if unavailable.
"""

from flask import Blueprint, request, jsonify
from models.database import get_db
from routes.auth_routes import get_current_user
from services.hash_service import hash_bytes
from services.blockchain_service import register_on_chain, verify_on_chain
from services.fraud_service import analyse
import datetime

doc_bp = Blueprint("docs", __name__)

ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}


@doc_bp.route("/upload", methods=["POST"])
def upload():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Login required"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]

    # Accept by extension too, since browsers sometimes send wrong MIME types
    filename_lower = f.filename.lower() if f.filename else ""
    mime_ok = f.mimetype in ALLOWED_TYPES
    ext_ok  = any(filename_lower.endswith(ext) for ext in (".pdf", ".png", ".jpg", ".jpeg", ".docx"))
    if not mime_ok and not ext_ok:
        return jsonify({"error": "Only PDF, DOCX, PNG, JPG files are allowed"}), 400

    file_bytes = f.read()

    # Step 1 — Hash the document
    doc_hash = hash_bytes(file_bytes)

    # Step 2 — Check for duplicates
    db  = get_db()
    dup = db.execute("SELECT id FROM documents WHERE doc_hash = ?", (doc_hash,)).fetchone()
    if dup:
        db.close()
        return jsonify({"error": "Document already registered", "hash": doc_hash}), 409

    # Step 3 — AI fraud detection
    fraud_score = analyse(file_bytes, f.filename)
    if fraud_score >= 0.7:
        status = "rejected"
    elif fraud_score >= 0.3:
        status = "flagged"
    else:
        status = "verified"

    # Step 4 — Register on blockchain (skip if rejected)
    tx_hash      = None
    block_number = None
    blockchain_used = False
    if status != "rejected":
        try:
            result       = register_on_chain(doc_hash)
            tx_hash      = result.get("tx_hash")
            block_number = result.get("block_number")
            blockchain_used = True
        except Exception as e:
            # Blockchain unavailable — keep status from fraud check, record in DB only
            print(f"Blockchain unavailable during upload: {e}")

    # Step 5 — Save to SQLite
    db.execute(
        """INSERT INTO documents
           (filename, doc_hash, tx_hash, block_number, fraud_score, status, uploader_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (f.filename, doc_hash, tx_hash, block_number,
         round(fraud_score, 4), status, user["id"]),
    )
    db.commit()
    db.close()

    return jsonify({
        "message":          f"Document processed — status: {status}",
        "hash":             doc_hash,
        "tx_hash":          tx_hash,
        "fraud_score":      round(fraud_score * 100, 1),
        "status":           status,
        "filename":         f.filename,
        "blockchain_used":  blockchain_used,
    }), 201


@doc_bp.route("/verify/<doc_hash>", methods=["GET"])
def verify(doc_hash):
    """
    Verify a document hash. Checks the blockchain first; if unavailable,
    falls back to the local database so the feature always works.
    """
    db = get_db()

    # Log the verification attempt
    db.execute("INSERT INTO verify_log (doc_hash, found) VALUES (?, 0)", (doc_hash,))
    db.commit()

    # Fetch database record first (needed regardless of blockchain result)
    record = db.execute(
        "SELECT * FROM documents WHERE doc_hash = ?", (doc_hash,)
    ).fetchone()
    record = dict(record) if record else None

    # Try blockchain
    blockchain_available = False
    blockchain_found     = False
    chain_timestamp      = None
    chain_uploader       = None
    try:
        result              = verify_on_chain(doc_hash)
        blockchain_available = True
        blockchain_found     = result.get("exists", False)
        chain_timestamp      = result.get("timestamp")
        chain_uploader       = result.get("uploader")
    except Exception as e:
        print(f"Blockchain unavailable during verify: {e}")

    # Decide whether the document is "found"
    if blockchain_available:
        found = blockchain_found
    else:
        # Database fallback: found if it was registered and not rejected
        found = record is not None and record["status"] in ("verified", "flagged", "pending")

    # Update verification log
    db.execute(
        "UPDATE verify_log SET found = ? WHERE doc_hash = ? AND found = 0",
        (1 if found else 0, doc_hash),
    )
    db.commit()
    db.close()

    response = {
        "hash":               doc_hash,
        "found":              found,
        "timestamp":          chain_timestamp,
        "uploader":           chain_uploader,
        "blockchain_used":    blockchain_available,
    }
    if record:
        response["filename"]    = record["filename"]
        response["status"]      = record["status"]
        response["fraud_score"] = record["fraud_score"]

    return jsonify(response)


@doc_bp.route("/my", methods=["GET"])
def my_docs():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Login required"}), 401

    db   = get_db()
    docs = db.execute(
        "SELECT * FROM documents WHERE uploader_id = ? ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    db.close()
    return jsonify([dict(d) for d in docs])
