from App.database import db

class Menu(db.Model):
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable = False)
    items = db.relationship('MenuBreadItem', backref='menu')
    drives = db.relationship('Drive', backref = 'menu')
    
    def __init__(self, name):
        self.name = name


    def list():
        return Menu.query.all()


    def get_bread_items(self):
        return [item.bread_item for item in self.items]
    
    def get_bread_items_str(self):
        bread_items = self.get_bread_items()
        if not bread_items:
            return "No items"
        return ", ".join([f"{bread.name} (${bread.price:.2f})" for bread in bread_items])