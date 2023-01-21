from datetime import datetime
from unibaza import db, login_manager
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
    __tablename__ = 'kontrakty'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numer = db.Column(db.SmallInteger, unique=True, nullable=True)
    nazwa = db.Column(db.String(30), unique=True, nullable=False)
    kraj = db.Column(db.String(3), unique=False, nullable=False)
    kolor = db.Column(db.String(30), nullable=False)
    skrzynie_ref = db.relationship('Skrzynie', backref='kontrakt')
    
    def __repr__(self):
        return f"{self.id}: {self.numer}-{self.nazwa} ({self.kraj} | {self.kolor}) "
    
class Skrzynie(db.Model):
    __tablename__ = 'skrzynie'
    id = db.Column(db.Integer, primary_key=True)
    zawartosc = db.Column(db.Text, nullable=False)
    szer = db.Column(db.Integer, nullable=True, default="")
    wys = db.Column(db.Integer, nullable=True, default="")
    dł = db.Column(db.Integer, nullable=True, default="")
    waga = db.Column(db.Integer, nullable=True, default="")
    autor = db.Column(db.String(25), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.now)
    kontrakt_id = db.Column(db.Integer, db.ForeignKey('kontrakty.id'), nullable=True)

    def __repr__(self):
        return f"{self.id}: {self.zawartosc} | {self.autor} | {self.data} | {self.kontrakt_id}"

class Queue(db.Model):
    __tablename__='kolejka'
    id = db.Column(db.Integer, primary_key=True)
    zadanie = db.Column(db.String(100), nullable=False)
    kontrakt = db.Column(db.String(30), nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    user = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), nullable=False, default='oczekujące')

class Realizacja(db.Model):
    __tablename__='realizacja'
    id = db.Column(db.Integer, primary_key=True)
    listorder = db.Column(db.Integer, autoincrement=True)
    moduł = db.Column(db.String(140))
    tarcica_stropy = db.Column(db.Integer, default=0)
    formatki_stropy = db.Column(db.Integer, default=0)
    podłoga = db.Column(db.Integer, default=0)
    sufit = db.Column(db.Integer, default=0)
    dach = db.Column(db.Integer, default=0)
    tarcica_sciany = db.Column(db.Integer, default=0)
    formatki_sciany = db.Column(db.Integer, default=0)
    sciany = db.Column(db.Integer, default=0)
    montaz = db.Column(db.Integer, default=0)
    odbior = db.Column(db.Integer, default=0)


