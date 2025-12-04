import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime, time, timedelta

from App.main import create_app
from App.database import db, create_db
from App.models import User, Resident, Driver, Admin, Area, Street, Drive, Stop, Item, DriverStock
from App.controllers import *
from App.models import User, Resident, Driver, Admin, Area, Street, Drive, Stop, Item, DriverStock, Menu, BreadItem, MenuBreadItem, Notification, StreetSubscription
from App.controllers import *
from App.controllers.Notification import create_notification



LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    # pure function no side effects or integrations called
    def test_user_getJSON(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        newuser = User("bob", password)
        assert newuser.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)

class ResidentUnitTests(unittest.TestCase):

    def test_new_resident(self):
        resident = Resident("john", "johnpass", 1, 2, 123)
        assert resident.username == "john"
        assert resident.password != "johnpass"
        assert resident.areaId == 1
        assert resident.streetId == 2
        assert resident.houseNumber == 123
        assert resident.inbox == []

    def test_resident_type(self):
        resident = Resident("john", "johnpass", 1, 2, 123)
        assert resident.type == "Resident"

    def test_resident_getJSON(self):
        resident = Resident("john", "johnpass", 1, 2, 123)
        resident_json = resident.get_json()
        self.assertDictEqual(resident_json, {"id":None, "username":"john", "areaId":1, "houseNumber":123, "inbox":[]})

    def test_receive_notif(self):
        resident = Resident("john", "johnpass", 1, 2, 123)
        resident.receive_notif("New msg")
        assert resident.inbox[-1].endswith("New msg")
        assert resident.inbox[-1].startswith("[")

    def test_view_inbox(self):
        resident = Resident("john", "johnpass", 1, 2, 123)
        resident.receive_notif("msg1")
        resident.receive_notif("msg2")
        assert len(resident.inbox) == 2
        assert resident.inbox[0].endswith("msg1")
        assert resident.inbox[1].endswith("msg2")
        assert resident.inbox[0].startswith("[")
        assert resident.inbox[1].startswith("[")
        
class DriverUnitTests(unittest.TestCase):

    def test_new_driver(self):
        driver = Driver("steve", "stevepass", "Busy", 2, 12)
        assert driver.username == "steve"
        assert driver.password != "stevepass"
        assert driver.status == "Busy"
        assert driver.areaId == 2
        assert driver.streetId == 12
        
    def test_driver_type(self):
        driver = Driver("steve", "stevepass", "Busy", 2, 12)
        assert driver.type == "Driver"

    def test_driver_getJSON(self):
        driver = Driver("steve", "stevepass", "Busy", 2, 12)
        driver_json = driver.get_json()
        self.assertDictEqual(driver_json, {"id":None, "username":"steve", "status":"Busy", "areaId":2, "streetId":12})

class AdminUnitTests(unittest.TestCase):

    def test_new_admin(self):
        admin = Admin("admin", "adminpass")
        assert admin.username == "admin"
        assert admin.password != "adminpass"

    def test_admin_type(self):
        admin = Admin("admin", "adminpass")
        assert admin.type == "Admin"

    def test_admin_getJSON(self):
        admin = Admin("admin", "adminpass")
        admin_json = admin.get_json()
        self.assertDictEqual(admin_json, {"id":None, "username":"admin"})

class AreaUnitTests(unittest.TestCase):

    def test_new_area(self):
        area = Area("Sangre Grande")
        assert area.name == "Sangre Grande"

    def test_area_getJSON(self):
        area = Area("Sangre Grande")
        area_json = area.get_json()
        self.assertDictEqual(area_json, {"id":None, "name":"Sangre Grande"})

class StreetUnitTests(unittest.TestCase):

    def test_new_street(self):
        street = Street("Picton Road", 8)
        assert street.name == "Picton Road"
        assert street.areaId == 8

    def test_street_getJSON(self):
        street = Street("Picton Road", 8)
        street_json = street.get_json()
        self.assertDictEqual(street_json, {"id":None, "name":"Picton Road", "areaId":8})

class DriveUnitTests(unittest.TestCase):

    def test_new_drive(self):
        drive = Drive(78, 2, 12, date(2025, 11, 8), time(11, 30), "Upcoming")
        assert drive.driverId == 78
        assert drive.areaId == 2
        assert drive.streetId == 12
        assert drive.date == date(2025, 11, 8)
        assert drive.time == time(11, 30)
        assert drive.status == "Upcoming"

    def test_drive_getJSON(self):
        drive = Drive(78, 2, 12, date(2025, 11, 8), time(11, 30), "Upcoming")
        drive_json = drive.get_json()
        self.assertDictEqual(drive_json, {"id":None, "driverId":78, "areaId":2, "streetId":12, "date":"2025-11-08", "time":"11:30:00", "status":"Upcoming"})

class StopUnitTests(unittest.TestCase):

    def test_new_stop(self):
        stop = Stop(1, 2)
        assert stop.driveId == 1
        assert stop.residentId == 2

    def test_stop_getJSON(self):
        stop = Stop(1, 2)
        stop_json = stop.get_json()
        self.assertDictEqual(stop_json, {"id":None, "driveId":1, "residentId":2})

class ItemUnitTests(unittest.TestCase):

    def test_new_item(self):
        item = Item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])
        assert item.name == "Whole-Grain Bread"
        assert item.price == 19.50
        assert item.description == "Healthy whole-grain loaf"
        assert item.tags == ["whole-grain", "healthy"]

    def test_item_getJSON(self):
        item = Item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])
        item_json = item.get_json()
        self.assertDictEqual(item_json, {"id":None, "name":"Whole-Grain Bread", "price":19.50, "description":"Healthy whole-grain loaf", "tags":["whole-grain", "healthy"]})

class DriverStockUnitTests(unittest.TestCase):

    def test_new_driverStock(self):
        driverStock = DriverStock(1, 2, 30)
        assert driverStock.driverId == 1
        assert driverStock.itemId == 2
        assert driverStock.quantity == 30

    def test_driverStock_getJSON(self):
        driverStock = DriverStock(1, 2, 30)
        driverStock_json = driverStock.get_json()
        self.assertDictEqual(driverStock_json, {"id":None, "driverId":1, "itemId":2, "quantity":30})

class MenuUnitTests(unittest.TestCase): ##new unit test start here

    def test_new_menu(self):

        menu = Menu("TestMenu")

        db.session.add(menu)
        db.session.commit()

        assert menu.id == 1
        assert menu.name == "TestMenu"

    def test_menu_list(self):

        menu1 = Menu("TestMenu1")
        menu2 = Menu("TestMenu2")

        db.session.add(menu1)
        db.session.add(menu2)

        db.session.commit()

        menus = Menu.list()

        assert len(menus) == 2
        assert any(menu.name == "TestMenu1" for menu in menus)
        assert any(menu.name == "TestMenu2" for menu in menus)

    def test_get_breadItem(self):

        menu = Menu("TestMenu")
        bread = BreadItem ("TestBread", 12.50)

        db.session.add(menu)
        db.session.add(bread)
        db.session.commit()

        menubreaditem = MenuBreadItem(menu.id, bread.id)
        db.session.add(menubreaditem)
        db.session.commit()

        items = menu.get_bread_items()

        assert len(items) == 1
        assert any (item.id == bread.id for item in items)



class BreadItemUnitTests(unittest.TestCase):

    def test_new_breadItem(self):

        bread = BreadItem ("TestBread", 12.50)

        db.session.add(bread)
        db.session.commit()

        assert bread.id == 1
        assert bread.name == "TestBread"

    def test_bread_list(self):

        bread1 = BreadItem ("TestBread1", 12.50)
        bread2 = BreadItem ("TestBread2", 12.50)
        
        db.session.add(bread1)
        db.session.add(bread2)
        db.session.commit()

        breads = BreadItem.list()

        assert len(breads) == 2
        assert any(bread.name == "TestBread1" for bread in breads)
        assert any(bread.name == "TestBread2" for bread in breads)

class MenuBreadItemUnitTests(unittest.TestCase):

    def test_new_menuBreadItem(self):

        menu = Menu("TestMenu")
        bread = BreadItem ("TestBread", 12.50)

        db.session.add(menu)
        db.session.add(bread)
        db.session.commit()

        menuBreadItem = MenuBreadItem(menu.id,bread.id)

        db.session.add(menuBreadItem)
        db.session.commit()

        storedMenuBreadItem = MenuBreadItem.query.filter_by(menu_id = menu.id,bread_id = bread.id).first()

        assert storedMenuBreadItem is not None      
        assert storedMenuBreadItem.menu_id == menu.id
        assert storedMenuBreadItem.bread_id == bread.id

    def test_menuBreadItem_list(self):
        
        menu1 = Menu("TestMenu1")
        bread1 = BreadItem ("TestBread1", 12.50)

        menu2 = Menu("TestMenu2")
        bread2 = BreadItem ("TestBread2", 12.50)

        db.session.add(menu1)
        db.session.add(bread1)
        db.session.add(menu2)
        db.session.add(bread2)
        db.session.commit()

        menuBreadItem1 = MenuBreadItem(menu1.id,bread1.id)
        menuBreadItem2 = MenuBreadItem(menu2.id,bread2.id)

        db.session.add(menuBreadItem1)
        db.session.add(menuBreadItem2)
        db.session.commit()

        menuBreadItems = MenuBreadItem.list()

        assert len(menuBreadItems) == 2
        assert any(item.menu_id == menu1.id for item in menuBreadItems)
        assert any(item.bread_id == bread1.id for item in menuBreadItems)
        assert any(item.menu_id == menu2.id for item in menuBreadItems)
        assert any(item.bread_id == bread2.id for item in menuBreadItems)

class NotificationUnitTests(unittest.TestCase):

    def test_create_notification(self):

        drive = Drive(78, 2, 12, date(2025, 11, 8), time(11, 30), "Upcoming")
        resident = Resident("frank", "frankpass", 1, 2, 123)

        db.session.add(drive)
        db.session.add(resident)
        db.session.commit()

        message = "This is a test message"
        notification = create_notification (message,resident.id, drive.id)

        db.session.add(notification)
        db.session.commit()

        assert notification.message == message
        assert notification.drive_id == drive.id
        assert notification.resident_id == resident.id

    def test_notification_list(self):

        drive1 = Drive(78, 2, 12, date(2025, 11, 8), time(11, 30), "Upcoming")
        resident1 = Resident("frank", "frankpass", 1, 2, 123)

        drive2 = Drive(78, 2, 12, date(2025, 12, 8), time(11, 30), "Upcoming")
        resident2 = Resident("hannah", "hannahpass", 1, 2, 123)

        db.session.add(drive1)
        db.session.add(resident1)
        db.session.add(drive2)
        db.session.add(resident2)
        db.session.commit()

        message = "This is a test message"
        notification1 = create_notification (message,resident1.id, drive1.id)
        notification2 = create_notification (message,resident2.id, drive2.id)

        db.session.add(notification1)
        db.session.add(notification2)
        db.session.commit()

        notifications = Notification.list()

        assert len(notifications) == 2
        assert any(notification.id == notification1.id for notification in notifications)
        assert any(notification.id == notification2.id for notification in notifications)
        assert any(notification.message == message for notification in notifications)
        
        
class StreetSubcriptionUnitTests(unittest.TestCase):

    def test_new_streetSubcription(self):

        street = Street("TestStreet", 1)
        db.session.add(street)
        db.session.commit()

        resident = Resident("frank", "frankpass", 1, street.id, 123)

        db.session.add(resident)
        db.session.commit()

        subcription1 = StreetSubscription (resident.id, street.id)

        db.session.add(subcription1)
        db.session.commit()


        subcription = StreetSubscription.query.filter_by(street_id = street.id,resident_id = resident.id).first()

        assert subcription is not None
        assert subcription.resident_id == resident.id
        assert subcription.street_id == street.id

    def test_get_subcribers_for_street(self):

        street = Street("TestStreet", 1)
        db.session.add(street)
        db.session.commit()

        resident1 = Resident("frank", "frankpass", 1, street.id, 123)
        resident2 = Resident("hannah", "hannahpass", 1, street.id, 123)

        db.session.add(resident1)
        db.session.add(resident2)
        db.session.commit()

        subcription1 = StreetSubscription (resident1.id, street.id)
        subcription2 = StreetSubscription (resident2.id, street.id)

        db.session.add(subcription1)
        db.session.add(subcription2)
        db.session.commit()

        subcriptions = StreetSubscription.get_subscribers_for_street(street.id)

        assert any(subcription.street_id == street.id for subcription in subcriptions)
        assert any(subcription.resident_id == resident1.id for subcription in subcriptions)
        assert any(subcription.resident_id == resident2.id for subcription in subcriptions)


'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="function")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    db.create_all()    
    yield app.test_client()
    db.drop_all()


class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "ronniepass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        create_user("bob", "bobpass")
        create_user("rick", "ronniepass")
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        create_user("rick", "ronniepass")
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"

    def test_login(self):
        create_user("ronnie", "ronniepass")
        user = user_login("ronnie", "ronniepass")
        assert user.username == "ronnie"

    def test_logout(self):
        create_user("ronnie", "ronniepass")
        user = user_login("ronnie", "ronniepass")
        user_logout(user)
        assert user.logged_in == False
        if isinstance(user, Driver):
            updated_user = get_user(user.id)
            assert updated_user.status == "Offline"


class ResidentsIntegrationTests(unittest.TestCase):
    
    def setUp(self):
        self.area = admin_add_area("St. Augustine")
        self.street = admin_add_street(self.area.id, "Warner Street")
        self.driver = admin_create_driver("driver1", "pass")
        self.menu = admin_create_menu("Menu1", None)
        self.resident = resident_create("john", "johnpass", self.area.id, self.street.id, 123)
        self.drive = driver_schedule_drive(self.driver, self.area.id, self.street.id, "2025-12-31", "11:30",self.menu.id)
        self.item = admin_add_item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])


    def test_request_stop(self):
        stop = resident_request_stop(self.resident, self.drive.id)
        self.assertIsNotNone(stop)

    def test_cancel_stop(self):
        stop = resident_request_stop(self.resident, self.drive.id)
        resident_cancel_stop(self.resident, stop.id)
        self.assertIsNone(Stop.query.filter_by(id=stop.id).first())

    def test_view_driver_stats(self):
        driver = resident_view_driver_stats(self.resident, self.driver.id)
        self.assertIsNotNone(driver)

    def test_view_stock(self):
        driver_update_stock(self.driver, self.item.id, 30)
        stock = resident_view_stock(self.resident, self.driver.id)
        self.assertIsNotNone(stock)

    def test_resident_subscribe(self):            # 1 Numbered from tests what I added
        subscription = resident_subscribe(self.resident)
        self.assertIsNotNone(subscription)
        # Test duplicate
        duplicate = resident_subscribe(self.resident)
        assert duplicate is None

    def test_resident_unsubscribe(self):              # 2
        resident_subscribe(self.resident)
        street_name, area_name = resident_unsubscribe(self.resident)
        self.assertIsNotNone(street_name)
        # unsubscribe when not subscribed before 
        result = resident_unsubscribe(self.resident)
        assert result == (None, None)

    def test_resident_get_subscriptions(self):         #3
        resident_subscribe(self.resident)
        subscriptions = resident_get_subscriptions(self.resident)
        assert len(subscriptions) == 1
        assert subscriptions[0].resident_id == self.resident.id


    def test_resident_get_notifications(self):             #4
   
        create_notification("Driver has arrived", self.resident.id, self.drive.id)
        notifications = resident_get_notifications(self.resident)
        assert len(notifications) == 1
        assert notifications[0].message == "Driver has arrived"


    def test_resident_get_available_drives(self):          #5
        drives = resident_get_available_drives(self.resident)
        # Should include the drive we created in setUp
        assert len(drives) >= 1
        assert all(d.status == "Upcoming" for d in drives)

    
   # Negative tests
    def test_resident_request_stop_invalid_drive(self):   #6
       with self.assertRaises(ValueError):
        resident_request_stop(self.resident, 999) 

    def test_resident_request_stop_duplicate(self):        #7
        resident_request_stop(self.resident, self.drive.id)
        with self.assertRaises(ValueError):
            resident_request_stop(self.resident, self.drive.id)

    def test_resident_cancel_stop_no_stop(self):           #8
        with self.assertRaises(ValueError):
            resident_cancel_stop(self.resident, 999)

    def test_resident_view_driver_stats_invalid_driver(self):   #9
        with self.assertRaises(ValueError):
            resident_view_driver_stats(self.resident, 999) 


class DriversIntegrationTests(unittest.TestCase):
                
    def setUp(self):
        self.area = admin_add_area("St. Augustine")
        self.street = admin_add_street(self.area.id, "Warner Street")
        self.driver = admin_create_driver("driver1", "pass")
        self.menu = admin_create_menu("Menu1", None)
        self.resident = resident_create("john", "johnpass", self.area.id, self.street.id, 123)
        self.drive = driver_schedule_drive(self.driver, self.area.id, self.street.id, "2025-12-31", "11:30", self.menu.id)
        self.stop = resident_request_stop(self.resident, self.drive.id)
        self.item = admin_add_item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])
        self.time = datetime.now() + timedelta(minutes=5)
        self.time_str = self.time.time().strftime("%H:%M")
        self.date = datetime.now().date().strftime("%Y-%m-%d")

    def test_schedule_drive(self):
        drive = driver_schedule_drive(self.driver, self.area.id, self.street.id, self.date ,self.time_str, self.menu.id)
        self.assertIsNotNone(drive)

    def test_cancel_drive(self):
        drive = driver_schedule_drive(self.driver, self.area.id, self.street.id, self.date , self.time_str,self.menu.id)
        driver_cancel_drive(self.driver, drive.id)
        assert drive.status == "Cancelled"

    def test_view_drives(self):
        drives = driver_view_drives(self.driver)
        self.assertIsNotNone(drives)

    def test_start_drive(self):
        driver_start_drive(self.driver, self.drive.id)
        drive = Drive.query.filter_by(id=self.drive.id).first()
        assert self.drive.status == "In Progress"
        assert self.driver.status == "Busy"

    def test_end_drive(self):
        driver_start_drive(self.driver, self.drive.id)
        driver_end_drive(self.driver)
        drive = Drive.query.filter_by(id=self.drive.id).first()
        assert self.drive.status == "Completed"
        assert self.driver.status == "Available"

    def test_view_requested_stops(self):
        stops = driver_view_requested_stops(self.driver, self.drive.id)
        self.assertIsNotNone(stops)
    
    def test_update_stock(self):
        newquantity = 30
        driver_update_stock(self.driver, self.item.id, newquantity)
        stock = DriverStock.query.filter_by(driverId=self.driver.id, itemId=self.item.id).first()
        assert stock.quantity == newquantity

    def test_view_stock(self):
        stock = driver_view_stock(self.driver)
        self.assertIsNotNone(stock)


     #Negative tests 
    def test_driver_schedule_drive_past_date(self):          #10
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError):
            driver_schedule_drive(self.driver, self.area.id, self.street.id, past_date, "11:30", self.menu.id)


    def test_driver_schedule_drive_invalid_format(self):     #11
        with self.assertRaises(ValueError):
            driver_schedule_drive(self.driver, self.area.id, self.street.id, "invalid-date", "11:30", self.menu.id)



    def test_driver_start_drive_already_in_progress(self):    #12
        driver_start_drive(self.driver, self.drive.id)
        another_drive = driver_schedule_drive(self.driver, self.area.id, self.street.id, "2025-12-31", "12:30", self.menu.id)
        with self.assertRaises(ValueError):
            driver_start_drive(self.driver, another_drive.id)


    def test_driver_end_drive_no_drive_in_progress(self):      #13
         with self.assertRaises(ValueError):
            driver_end_drive(self.driver)

    def test_driver_update_stock_invalid_item(self):          #14
        with self.assertRaises(ValueError):
            driver_update_stock(self.driver, 999, 30)




class AdminsIntegrationTests(unittest.TestCase):
    
    def setUp(self):
        self.test_area = admin_add_area("AdminTest Area")
        self.test_street = admin_add_street(self.test_area.id, "AdminTest Street") 
        self.test_driver = admin_create_driver("admintestdriver", "pass")
        self.test_menu = admin_create_menu("AdminTest Menu", None)
    
    def test_create_driver(self):
        driver = admin_create_driver("driver1", "driverpass")
        assert Driver.query.filter_by(id=driver.id).first() != None

    def test_delete_driver(self):
        driver = admin_create_driver("driver1", "driverpass")
        admin_delete_driver(driver.id)
        assert Driver.query.filter_by(id=driver.id).first() == None

    def test_add_area(self):
        area = admin_add_area("Port-of-Spain")
        assert Area.query.filter_by(id=area.id).first() != None

    def test_delete_area(self):
        area = admin_add_area("Port-of-Spain")
        admin_delete_area(area.id)
        assert Area.query.filter_by(id=area.id).first() == None

    def test_view_all_areas(self):
        admin_add_area("Port-of-Spain-Unique")
        admin_add_area("Arima-Unique") 
        admin_add_area("San Fernando-Unique")
        areas = admin_view_all_areas()
        assert areas != None
        assert len(areas) == 4

    def test_add_street(self):
        area = admin_add_area("Port-of-Spain")
        street = admin_add_street(area.id, "Fredrick Street")
        assert Street.query.filter_by(id=street.id).first() != None

    def test_delete_street(self):
        area = admin_add_area("Port-of-Spain")
        street = admin_add_street(area.id, "Fredrick Street")
        admin_delete_street(area.id, street.id)
        assert Street.query.filter_by(id=street.id, areaId=area.id).first() == None

    def test_view_all_streets(self):  
        for street in Street.query.all():
            if street.name != "AdminTest Street":
                db.session.delete(street)
                db.session.commit()
        
        area = admin_add_area("Port-of-Spain-Streets")
        admin_add_street(area.id, "Fredrick Street")
        admin_add_street(area.id, "Warner Street")
        admin_add_street(area.id, "St. Vincent Street")
        streets = admin_view_all_streets()
        assert streets != None
        assert len(streets) == 4

    def test_add_item(self):
        item = admin_add_item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])
        assert Item.query.filter_by(id=item.id).first() != None

    def test_delete_item(self):
        item = admin_add_item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])
        admin_delete_item(item.id)
        assert Item.query.filter_by(id=item.id).first() == None

    def test_view_all_items(self):
        admin_add_item("Whole-Grain Bread", 19.50, "Healthy whole-grain loaf", ["whole-grain", "healthy"])
        admin_add_item("White Milk Bread", 12.00, "Soft and fluffy white milk bread", ["white", "soft"])
        admin_add_item("Whole-Wheat Bread", 15.00, "Nutritious whole-wheat bread", ["whole-wheat", "nutritious"])
        items = admin_view_all_items()
        assert items != None
        assert len(items) == 3
        
    
    def test_admin_schedule_drive(self):         #15
        drive = admin_schedule_drive(self.test_driver, self.test_area.id, self.test_street.id, "2025-12-31", "11:30", self.test_menu.id)
        self.assertIsNotNone(drive)
        assert drive.status == "Upcoming"


    def test_admin_view_menus(self):            #16
        menus = admin_view_menus()
        assert isinstance(menus, list)
        assert len(menus) >= 1


    def test_admin_create_menu_with_items(self):   #17
        bread1 = BreadItem("Sourdough", 6.99)
        bread2 = BreadItem("Rye", 5.49)
        db.session.add_all([bread1, bread2])
        db.session.commit()
        
        menu = admin_create_menu("Special Menu", [bread1.id, bread2.id])
        self.assertIsNotNone(menu)
        assert menu.name == "Special Menu"
    
        bread_items = menu.get_bread_items()
        assert len(bread_items) == 2
        assert bread_items[0].name in ["Sourdough", "Rye"]

    
    # Negative tests
    def test_admin_create_driver_duplicate_username(self):      #18
        admin_create_driver("testdriverunique", "pass")
        with self.assertRaises(ValueError):
            admin_create_driver("testdriverunique", "pass2")  

    def test_admin_delete_driver_invalid_id(self):              #19
        with self.assertRaises(ValueError):
            admin_delete_driver(999)  

    def test_admin_add_street_invalid_area(self):           #20
         with self.assertRaises(ValueError):
            admin_add_street(999, "Test Street")  

    def test_admin_delete_area_invalid_id(self):         #21
        with self.assertRaises(ValueError):
            admin_delete_area(999)  

    def test_admin_delete_street_invalid_ids(self):     #22
        with self.assertRaises(ValueError):
            admin_delete_street(999, 1) 

        area = admin_add_area("Test Area one")
        with self.assertRaises(ValueError):
            admin_delete_street(area.id, 999)  

    def test_admin_delete_item_invalid_id(self):         #23
        with self.assertRaises(ValueError):
            admin_delete_item(999) 



class ObserverPatternIntegrationTests(unittest.TestCase):
    
    def setUp(self):
        self.area = admin_add_area("Test Area")
        self.street = admin_add_street(self.area.id, "Test Street")
        self.driver = admin_create_driver("testdriver", "pass")
        self.menu = admin_create_menu("Test Menu", None)
        self.resident = resident_create("testuser", "pass", self.area.id, self.street.id, 123)
    
    def test_observer_pattern_notification_creation(self):
        
        resident_subscribe(self.resident)
        
        # Will trigger notif
        drive = driver_schedule_drive(self.driver, self.area.id, self.street.id, "2025-12-31", "11:30", self.menu.id)
        
        # Notif created
        notifications = resident_get_notifications(self.resident)
        assert len(notifications) > 0
        assert any(n.drive_id == drive.id for n in notifications)
        
        notification = notifications[0]
        assert "Alert: Drive" in notification.message
        assert self.street.name in notification.message
        assert self.area.name in notification.message


    def test_street_subscription_get_subscribers(self):
    
        resident_subscribe(self.resident)
    
        subscribers = StreetSubscription.get_subscribers_for_street(self.street.id)
        assert subscribers.count() == 1
        assert subscribers.first().resident_id == self.resident.id