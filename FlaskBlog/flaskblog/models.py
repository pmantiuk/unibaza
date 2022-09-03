from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Kontrakty(db.Model):
    id = db.Column(db.SmallInteger, primary_key=True)
    nazwa = db.Column(db.String(30), unique=True, nullable=False)
    kolor = db.Column(db.String(30), nullable=False)
    skrzynie = db.relationship('BazaSkrzyń', backref='kontrakt', lazy=True)
    
    def __repr__(self):
        return f"Kontrakty('{self.id}', '{self.nazwa}', '{self.kolor}')"
    
class BazaSkrzyń(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zawartość = db.Column(db.Text, nullable=False)
    kto = db.Column(db.String(25), nullable=False)
    kiedy = db.Column(db.DateTime, nullable=False, default=datetime.now)
    contract_id = db.Column(db.Integer, db.ForeignKey('kontrakty.id'), nullable=False)

    def __repr__(self):
        return f"Baza skrzyń('{self.id}', '{self.zawartość}')"


