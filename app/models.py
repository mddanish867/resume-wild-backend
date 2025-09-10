from . import db
from datetime import datetime
import uuid

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    original_path = db.Column(db.String(255), nullable=False)
    optimized_path = db.Column(db.String(255), nullable=True)
    job_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields for tracking
    optimization_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    keywords_added = db.Column(db.Integer, default=0)
    original_filename = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Resume {self.id} - User {self.user_id}>'
    
    def to_dict(self):
        """Convert resume object to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_path': self.original_path,
            'optimized_path': self.optimized_path,
            'job_description': self.job_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'optimization_status': self.optimization_status,
            'keywords_added': self.keywords_added,
            'original_filename': self.original_filename
        }
    
    def update_status(self, status, keywords_count=None):
        """Update optimization status"""
        self.optimization_status = status
        self.updated_at = datetime.utcnow()
        if keywords_count is not None:
            self.keywords_added = keywords_count