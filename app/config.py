import os,json

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Read roles and organizations from environment variables
    ROLES = os.getenv('ROLES').split(',')
    ORGANIZATIONS = json.loads(os.getenv('ORGANIZATIONS'))

    # WorkOS settings
    WORKOS_CLIENT_ID = os.getenv('WORKOS_CLIENT_ID')
    WORKOS_API_KEY = os.getenv('WORKOS_API_KEY')
    WORKOS_WEBHOOKS_SECRET = os.getenv('WORKOS_WEBHOOK_SECRET')