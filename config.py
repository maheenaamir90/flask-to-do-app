import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_DATABASE_URI = "sqlite:///todo.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Security fix (CSRF/session hardening): do not send session cookies on
    # cross-site subrequests to reduce CSRF risk.
    SESSION_COOKIE_SAMESITE = "Lax"
