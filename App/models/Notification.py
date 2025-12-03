from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from App.database import db


class Notification(db.Model):
    __tablename__ = "notification"
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(128), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
   
    def __init__(self, message, resident_id, drive_id):
        self.message = message
        self.resident_id = resident_id
        self.drive_id = drive_id
        self.timestamp = datetime.now()

    
    def list():
        return Notification.query.all()