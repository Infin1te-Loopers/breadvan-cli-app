from App.database import db
from App.controllers.Notification import create_notification
from .observer import Observer

class residentObserver(Observer):


    def __init__(self, residentId):
        self.residentId = residentId

    def update(self, drive):
        message = f'Alert: Drive {drive.id} would be coming to you on {drive.street.name}, {drive.street.area.name} on {drive.date} at {drive.time}.'
        message += f'\nMENU: {drive.menu.name} - Items: {drive.menu.get_bread_items_str()}'
        new_notification = create_notification(message, self.residentId, drive.id)
        return new_notification
