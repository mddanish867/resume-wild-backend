from . import db
from datetime import datetime
import uuid

class Resume(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)
    original_path = db.Column(db.String, nullable=False)
    optimized_path = db.Column(db.String, nullable=True)
    job_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)