from workos import WorkOSClient
import logging
from app.config import Config

class WorkOSService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workos_client = WorkOSClient(
            api_key=Config.WORKOS_API_KEY,client_id=Config.WORKOS_CLIENT_ID
        )

    def create_user(self, email, first_name, last_name, organization_id, role):
        create_user_payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        #TODO: add error handling e.g. in case user already exists in WorkOS
        workos_user = self.workos_client.user_management.create_user(**create_user_payload)
        self.workos_client.user_management.create_organization_membership(
            user_id=workos_user.id,
            organization_id=organization_id,
            role_slug=role)
        return workos_user.id

    def get_users(self, filters=None, sort=None, page=None):
        response = self.workos_client.user_management.list_users()
        return response.model_dump_json()

    def has_valid_signature(self, request, signature_header):
        try:
            self.workos_client.webhooks.verify_event(
                event_body=request.get_data(),
                event_signature=signature_header,
                secret=Config.WORKOS_WEBHOOKS_SECRET,
            )
            return True
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False