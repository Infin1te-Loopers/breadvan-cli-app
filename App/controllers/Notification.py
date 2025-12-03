from App.models import Notification
from App.database import db

def create_notification(message, resident_id, drive_id):
    new_notification = Notification(message, resident_id, drive_id)
    db.session.add(new_notification)
    db.session.commit()
    return new_notification