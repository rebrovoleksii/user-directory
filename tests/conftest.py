import pytest
from unittest.mock import patch, MagicMock
from flask.cli import load_dotenv

TEST_ORGANIZATION_NAME = 'Test Organization'
TEST_ORGANIZATION_ID = 'test_organization_id'
USER_DEFAULT_EMAIL = 'j.test@example.com'

@pytest.fixture
def app():
    load_dotenv()

    # load environment variables before importing the app
    from app import create_app
    from app.database import db
    from app.models.user import User

    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    with app.app_context():
        db.create_all()
        default_user = User(
            email=USER_DEFAULT_EMAIL,
            first_name='John',
            last_name='Test',
            organization_name=TEST_ORGANIZATION_NAME,
            organization_id=TEST_ORGANIZATION_ID,
            role='admin')
        db.session.add(default_user)
        db.session.commit()

        with patch('app.WorkOSService', new=MagicMock()):
            yield app;
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
