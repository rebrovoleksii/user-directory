from flask import Flask, g

from app.config import Config
from app.healthz.routes import healthz_bp
from app.users.routes import users_bp
from app.webhooks.routes import webhooks_bp
from app.workos_service import WorkOSService
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    #TODO: db migration should be implemented using Flask-Migrate
    with app.app_context():
        db.create_all()

    app.register_blueprint(healthz_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(users_bp)

    @app.before_request
    def load_dependencies():
        g.workos_service = WorkOSService()

    return app