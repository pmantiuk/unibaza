import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, make_response, jsonify
from unibaza import app, db, bcrypt, configuration
from unibaza.forms import RegistrationForm, LoginForm, AddCrate, UpdateAccountForm, PostForm, AddContract, PickContract
from unibaza.models import User, Post, Skrzynie, Kontrakty, Queue, Realizacja, Metadane
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import update


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    db.create_all()
    return render_template('home.html')

# sortowalny harmonogram z zaawansowaniem prac
@app.route("/", methods=['GET', 'POST'])
@app.route("/schedule", methods=['GET', 'POST'])
@login_required
def plan():
    # pobieram z bazy danych 'unihouse.db' tabelę 'realizacja' wysortowaną po kolumnie 'listorder'
    realizacja = Realizacja.query.order_by('listorder').all()
    # z pliku konfiguracyjnego pobieram list zawierające dane odnośnie używanych ikon i nazwa kolumn w tabeli realizacji
    obszary = configuration.obszary
    headers = configuration.headers
    # dokonuje zmiany statusu dla odpowiedniego modułu i operacji w bazie danych 'unihouse.db'
    if request.method == 'POST':
        id = request.form['id']
        operacja = request.form['operacja']
        moduł = Realizacja.query.filter(Realizacja.id == id).first()
        if request.form['status'] == 'rozpoczęte':
            setattr(moduł, operacja, 1)
            db.session.commit()
        elif request.form['status'] == 'zakończone':
            setattr(moduł, operacja, 2)
            db.session.commit()
        else:
            setattr(moduł, operacja, 0)
            db.session.commit()
    return render_template('schedule.html', realizacja=realizacja, obszary=obszary, headers=headers, username=current_user.username)

@app.route("/contracts_set", methods =['GET', 'POST'])
@login_required
def contracts_set():
    form = PickContract()
    if form.validate_on_submit():
        nazwa = form.kontrakt.data.partition('- ')[2]
        return redirect(url_for('crates_set', nazwa=nazwa))
    kontrakt = Kontrakty.query.order_by(Kontrakty.numer).all()
    return render_template('contracts.html', kontrakty = kontrakt, form=form)

@app.route("/crates_set/<nazwa>", methods=['GET', 'POST'])
@login_required
def crates_set(nazwa):
    form_add = AddCrate()
    kontrakt = Kontrakty.query.filter(Kontrakty.nazwa==nazwa).first().skrzynie_ref
    if form_add.validate_on_submit():
        z = int(form_add.ilość.data)
        for x in range(1, z+1):
            skrzynia = Skrzynie(zawartosc=form_add.content.data, autor=current_user.username, kontrakt_id = Kontrakty.query.filter(Kontrakty.nazwa==nazwa).first().id)
            db.session.add(skrzynia)
            db.session.commit()
        flash('Twoje skrzynie zostały pomyślnie dodane do bazy Byczku!', 'success')
        return redirect(url_for('crates_set', nazwa=nazwa))
    if request.method == 'POST' and ((request.form.get("user")==current_user.username) or (current_user.username in configuration.admins)) :
        obiekt = Skrzynie.query.filter(Skrzynie.id==request.form.get("sk")).first()
        obiekt.zawartosc = request.form.get('content')
        obiekt.szer = request.form.get('szerokość')
        obiekt.wys = request.form.get('wysokość')
        obiekt.dł = request.form.get('długość')
        obiekt.waga = request.form.get('waga')
        db.session.commit()
        flash('Pomyślnie zedytowano skrzynie!', 'success')
        return redirect(url_for('crates_set', nazwa=nazwa))
    elif request.method == 'POST':
        flash('Niestety nie masz uprawnień do edycji tej skrzyni.', 'warning')
        return redirect(url_for('crates_set', nazwa=nazwa))
    return render_template('crates_set.html', skrzynie = kontrakt, nazwa=nazwa, form_add=form_add)

@app.route("/add_contract", methods =['GET', 'POST'])
@login_required
def addcontract():
    form = AddContract()
    if form.validate_on_submit():
        kontrakt = Kontrakty(numer=form.numer.data, nazwa=form.nazwa.data, kraj=form.kraj.data, kolor=form.kolor.data)
        db.session.add(kontrakt)
        db.session.commit()
        flash('Pomyślnie dodano kontrakt do bazy!', 'success')
        return redirect(url_for('contracts_set'))
    return render_template('addcontract.html', form=form)

@app.route("/prints")
def wydruki():
    return render_template('formatowka/wydruki.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Twoje konto zostało utworzone! Teraz będziesz w stanie się zalogować.', 'success')
        return redirect (url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Logowanie nie powiodło się. Proszę sprawdź czy wpisałeś poprawną nazwę użytkownika i hasło.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/contract_management")
def contr_manage():
    return render_template('contract_management.html', title='Zarządzanie kontraktami')

@app.route("/wyloguj")
def wyloguj():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Twoje konto zostało zaktualizowane!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post został dodany!.', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                            form=form, legend='Nowy post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Twój post został zaktualizowany!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Twój post został usunięty!', 'success')
    return redirect(url_for('home'))

@app.route("/queue", methods=['POST','GET'])
def queue():
    zadania = Queue.query.order_by('id').all()
    if request.method == 'POST' and request.form.get('zadanie'):
        deadline = datetime.strptime(request.form.get('cutting_date'),"%Y-%m-%dT%H:%M")
        obiekt = Queue(zadanie=request.form.get('zadanie'), kontrakt=request.form.get('kontrakt'), deadline=deadline, user=current_user.username)
        db.session.add(obiekt)
        db.session.commit()
        print('To działanie dodania nowego zadania')
        return redirect(url_for('queue'))
    elif request.method == 'POST' and request.form.get('idnum') and request.form.get('user')==current_user.username:
        id = request.form.get('idnum')
        obiekt=Queue.query.filter(Queue.id==id).first()
        db.session.delete(obiekt)
        db.session.commit()
        flash('Pomyślnie usunięto zadanie!', 'success')
        return redirect(url_for('queue'))
    elif request.method == 'POST':
        flash('Nie możesz zadań, których autorem nie jesteś!', 'warning')
    return render_template('queue.html', zadania=zadania)

    # if request.method == 'POST' and ((request.form.get("user")==current_user.username) or (current_user.username in configuration.admins)) :
    #     obiekt = Skrzynie.query.filter(Skrzynie.id==request.form.get("sk")).first()
    #     obiekt.zawartosc = request.form.get('content')
    #     obiekt.szer = request.form.get('szerokość')
    #     obiekt.wys = request.form.get('wysokość')
    #     obiekt.dł = request.form.get('długość')
    #     obiekt.waga = request.form.get('waga')
    #     print(obiekt.szer)
    #     db.session.commit()
    #     flash('Pomyślnie zedytowano skrzynie!', 'success')
    #     return redirect(url_for('crates_set', nazwa=nazwa))
    # elif request.method == 'POST':
    #     flash('Niestety nie masz uprawnień do edycji tej skrzyni.', 'warning')
    #     return redirect(url_for('crates_set', nazwa=nazwa))

@app.route("/hundeggery")
def hundeggery():
    pass
    return render_template('queue.html')

@app.route("/updateList",methods=["POST","GET"])
def updateList():
    if request.method == 'POST':
        number_of_rows = db.session.query(Realizacja.id).count()
        getorder = request.form['order']
        order = getorder.split(",", number_of_rows)
        count=0
        for value in order:
            count +=1
            obiekt = Realizacja.query.filter(Realizacja.id==value).first()
            obiekt.listorder = count
        db.session.commit()
    return jsonify('Zaktualizowano!')