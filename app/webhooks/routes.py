from flask import Blueprint, Response, request, g
from app.database import db
from app.models.user import User
import logging


webhooks_bp = Blueprint('webhooks', __name__)
logger = logging.getLogger(__name__)

@webhooks_bp.route('/webhook/user-updated/diud67', methods=['POST'])
def webhook_user_updated():
    """
    This endpoint is called by WorkOS when a user is updated in the WorkOS dashboard.
    :return: 200 OK in case signature is invalid, user is not found in the DB or update is successful
             503 Service Unavailable in case can't update the user in the DB
    """
    # TODO: add idempotency check e.g. by storing the event_id in the Redis cache (https://workos.com/docs/events/data-syncing/webhooks/best-practices/ignore-duplicate-events)
    signature_header = request.headers["WorkOS-Signature"]
    if not g.workos_service.has_valid_signature(request, signature_header):
        return Response(status=200)

    data = request.get_json().get('data')
    user = db.session.query(User).filter_by(reference_id=data['id']).first()
    if not user:
        logger.warning(f"User with reference_id %{data['id']}% not found in DB")
        return Response(status=200)

    try:
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        db.session.commit()
    except Exception as e:
        logger.error(f"Error while updating user: {e}")
        return Response(status=503)

    return Response(status=200)