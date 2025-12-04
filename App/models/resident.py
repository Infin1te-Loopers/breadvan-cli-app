from datetime import datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON

from App.database import db
from App.models.drive import Drive
from .user import User
# Remove: from .driver import Driver  # This causes circular import
from .stop import Stop

from .StreetSubscription import StreetSubscription
from .Notification import Notification
MAX_INBOX_SIZE = 20


class Resident(User):
    __tablename__ = "resident"

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    areaId = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    streetId = db.Column(db.Integer,db.ForeignKey('street.id'),nullable=False)
    houseNumber = db.Column(db.Integer, nullable=False)
    inbox = db.Column(MutableList.as_mutable(JSON), default=[])
    notifications = db.relationship('Notification', backref='resident')
    subscriptions = db.relationship('StreetSubscription', backref='resident')
    stops = db.relationship('Stop', back_populates='resident')

    __mapper_args__ = {
        "polymorphic_identity": "Resident",
    }
    

    def list():
        return Resident.query.all()

    def get_by_id(id):
        return Resident.query.get(id)

    def __init__(self, username, password, areaId, streetId, houseNumber):
        super().__init__(username, password)
        self.areaId = areaId
        self.streetId = streetId
        self.houseNumber = houseNumber

    def get_json(self):
        user_json = super().get_json()
        user_json['areaId'] = self.areaId
        user_json['houseNumber'] = self.houseNumber
        user_json['inbox'] = self.inbox
        return user_json

    def request_stop(self, driveId):
        try:
            new_stop = Stop(driveId=driveId, residentId=self.id)
            db.session.add(new_stop)
            db.session.commit()
            return (new_stop)
        except Exception:
            db.session.rollback()
            return None

    def cancel_stop(self, stopId):
        stop = Stop.query.get(stopId)
        if stop:
            db.session.delete(stop)
            db.session.commit()
        return

    def receive_notif(self, message, drive_id=None):
      
      notification = Notification(message=message, resident_id=self.id, drive_id=drive_id)
      db.session.add(notification)
    
      # keeping inbox JSON logic incase
      if self.inbox is None:
        self.inbox = []

      if len(self.inbox) >= MAX_INBOX_SIZE:
        self.inbox.pop(0)

      timestamp = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
      notif = f"[{timestamp}]: {message}"
      self.inbox.append(notif)
    
      db.session.commit()
      return notification


    def view_inbox(self):
        return self.inbox

    def view_driver_stats(self, driverId):
        # Lazy import to avoid circular dependency
        from .driver import Driver
        driver = Driver.query.get(driverId)
        return driver

