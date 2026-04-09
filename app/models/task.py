from datetime import datetime, timezone

from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    # Use timezone-aware UTC timestamps to avoid deprecated utcnow usage.
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", back_populates="tasks")
