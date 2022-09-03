from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo,  ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Dołącz do nas Byczku!')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ten użytkownik już istnieje. Wybierz inną nazwę użytkownika.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ten email jest już zajęty. Wybierz inny adres email.')
    
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired()])
    remember =  BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class AddCrate(FlaskForm):
    kontrakt = SelectField('Wybierz kontrakt', choices=['Małkinia', 'Kernen', 'Kunzeslau', 'Kalbach',
                        'Kriftel'],
                        validators=[DataRequired()])
    ilość = SelectField('Określ ilość skrzyń', choices=[0,1,2,3,4],
                        validators=[DataRequired()])
    content = TextAreaField('Wprowadź zawartość', 
                            validators=[DataRequired()])
    submit = SubmitField('Generuj numery')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Zmień avatar', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Aktualizuj')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ten użytkownik już istnieje. Wybierz inną nazwę użytkownika.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ten email jest już zajęty. Wybierz inny adres email.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Publikuj')
    
    
