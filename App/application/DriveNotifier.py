from .Subject import Subject
from App.models.StreetSubscription import StreetSubscription
from App.application.residentObserver import *

class DriveNotifier(Subject):

    def __init__(self):
        super().__init__()
    
    def attach(self, observer):
        super().attach(observer)

    def detach(self, observer):
        super().detach(observer)

    def notify(self, drive):

        subscriptions = StreetSubscription.get_subscribers_for_street(drive.streetId)

        for subscription in subscriptions:
            
            observer = residentObserver(residentId=subscription.resident_id)
            self.attach(observer)
            
        for observer in self._observers:
            observer.update(drive)

        self._observers.clear()