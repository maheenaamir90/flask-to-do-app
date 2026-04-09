from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    # Security fix (CSRF): enable global CSRF protection for all unsafe methods.
    csrf.init_app(app)

    @app.after_request
    def add_security_headers(response):
        # Security fix (Clickjacking): deny rendering the app inside iframes.
        response.headers["X-Frame-Options"] = "DENY"
        # Security fix (Clickjacking): modern CSP equivalent for all ancestors.
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        return response

    from app.models import User
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    with app.app_context():
        db.create_all()

    return app
