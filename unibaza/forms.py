from email.policy import default
from unicodedata import numeric
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo,  ValidationError
from unibaza import configuration
from unibaza.models import User, Kontrakty

class PickContract(FlaskForm):
    kontrakt = SelectField('Wybierz kontrakt',choices=sorted([str(x.numer) + ' - ' + x.nazwa for x in Kontrakty.query.all()]))
    submit = SubmitField('Przejdź')

class AddCrate(FlaskForm):
    ilość = SelectField('Określ ilość skrzyń jaką chcesz pobrać', choices=[x for x in range(1,11)],
                        validators=[DataRequired()])
    content = TextAreaField('Wprowadź zawartość (wpisz to co będzie znajdować się w skrzyniach, na późniejszym etapie można to edytować)')
    submit = SubmitField('Dodaj')

class AddContract(FlaskForm):
    numer = StringField('Podaj numer kontraktu', 
                        validators=[DataRequired()])
    nazwa = StringField('Podaj nazwę kontraktu', 
                        validators=[DataRequired()])
    kraj = SelectField('Wybierz kraj', choices=sorted(configuration.kraje),
                        validators=[DataRequired()])
    kolor = SelectField('Wybierz kolor', choices=sorted(configuration.kolory),
                        validators=[DataRequired()])
    submit = SubmitField('Gotowe')

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', 
                             validators=[DataRequired()])
    confirm_password = PasswordField('Potwierdź hasło', 
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
    username = StringField('Nazwa użytkownika',
                        validators=[DataRequired()])
    password = PasswordField('Hasło', 
                             validators=[DataRequired()])
    remember =  BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')
    

class UpdateAccountForm(FlaskForm):
    username = StringField('Nazwa użytkownika', 
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
    
    
