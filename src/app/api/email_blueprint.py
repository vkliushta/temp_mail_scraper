"""email blueprint module"""

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from src.app.db.models import Email, EmailAddress
from src.app.extensions import db
from src.scraper.tasks import refresh_email_task

blueprint = Blueprint("email", __name__, url_prefix="/api")


@blueprint.route("/email", methods=["GET"])
def current_email():
    email = db.session.execute(select(EmailAddress).order_by(EmailAddress.time_created.desc())).scalars().first()
    if not email:
        return jsonify({"error": "No email found"}), 404

    return jsonify({"email": email.email})


@blueprint.route('/inbox', methods=['GET'])
def get_inbox():
    limit = request.args.get('limit', type=int)
    query = select(Email).order_by(Email.time_received.desc())
    if not limit:
        limit = 100
    query = query.limit(limit)
    
    emails = db.session.execute(query).scalars().all()
    
    return jsonify([{
        "sender": email.sender,
        "subject": email.subject,
        "time": email.time_received,
        "id": email.id
    } for email in emails])


@blueprint.route('/email/<int:id>', methods=['GET'])
def get_email_by_id(id):
    email = db.session.get(Email, id)
    if email:
        return jsonify(email.body)
    return jsonify({"error": "Email not found"}), 404


@blueprint.route("/email/refresh", methods=["POST"])
def refresh_email():
    task = refresh_email_task.delay()

    try:
        email = task.get(timeout=20)
    except Exception:
        return jsonify({"error": "Email refresh timeout"}), 500

    return jsonify({"email": email})
