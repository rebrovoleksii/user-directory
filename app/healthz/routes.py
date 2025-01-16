from flask import Blueprint, jsonify

healthz_bp = Blueprint('healthz', __name__)

@healthz_bp.route('/healthz', methods=['GET'])
def health_check():
    """
    Health check endpoint used by orchestration tools to determine if the service is running
    :return: 200 OK if the service is healthy and 503 Service Unavailable otherwise
    """
    #TODO: Split the health check into readiness and liveness probes.
    # Readiness might include DB connection, WorkOS API key valididy, etc.
    # Liveness probe just makes sure API can respond to requests
    return jsonify({'status': 'healthy'}), 200