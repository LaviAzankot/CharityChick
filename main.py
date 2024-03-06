import os
from flask import Flask, render_template, redirect, url_for, flash, request
from forms import CreatePostForm, RegisterForm, LoginForm, SearchForm, CommentForm
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, desc
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import string
from random import choice
from smtplib import SMTP


MY_EMAIL = os.environ.get('EMAIL') 
PASSWORD = os.environ.get('PASSWORD')

# Configure Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# Configure SQLAlchemy
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URI')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# ----------------- TABLES -----------------
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    address_url: Mapped[str] = mapped_column(String(500), nullable=False)


class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    condition: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    area: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    address_url: Mapped[str] = mapped_column(String, nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)

    author_name: Mapped[str] = mapped_column(String, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("posts.id"))


with app.app_context():
    db.create_all()


UPPER_CASE = string.ascii_uppercase
LOWER_CASE = string.ascii_lowercase
NUMBERS = string.digits
SYMBOLS = string.punctuation


def generate_password(length):
    all_strings = [UPPER_CASE, LOWER_CASE, NUMBERS, SYMBOLS]
    password = [choice(choice(all_strings)) for n in range(length)]
    password = ''.join(password)
    return password


# ----------------- PAGES -----------------

# Security (Register, Login, Logout)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(
        password=generate_password(8)
    )
    if form.validate_on_submit():
        # Check if the user already signed up with that email
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        # Encrypt the password
        hashed_and_salted_password = generate_password_hash(
            password=form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        # Add new user to db and login
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_and_salted_password,
            area=form.area.data,
            address=form.address.data,
            address_url=form.address_url.data
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check in User where the email corresponds to the email that was entered
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Email does not exist
        if not user:
            flash("This email does not exist, try to sign up instead.")
            return redirect(url_for('register'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash("This password is incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Home
@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    # Search posts by query
    if form.validate_on_submit():
        result = db.session.execute(
            db.select(Post).where(Post.category == form.category.data and Post.area == form.area.data).order_by(
                desc(Post.id)))
        posts = result.scalars().all()
        return render_template('index.html', posts=posts, form=form)

    # Get all posts
    with app.app_context():
        result = db.session.execute(db.select(Post).order_by(desc(Post.id)))
        posts = result.scalars().all()
    return render_template('index.html', posts=posts, form=form)


# Posts
@app.route('/post', methods=['GET', 'POST'])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        # Add new post to db
        with app.app_context():
            new_post = Post(
                title=form.title.data,
                author_id=current_user.id,
                category=form.category.data,
                condition=form.condition.data,
                content=form.content.data,
                img_url=form.img_url.data,
                date=datetime.now().strftime("%B %d, %Y"),
                name=current_user.name,
                area=current_user.area,
                address=current_user.address,
                address_url=current_user.address_url
            )
            db.session.add(new_post)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('make_post.html', form=form)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = CreatePostForm(
        title=post.title,
        category=post.category,
        condition=post.condition,
        img_url=post.img_url,
        content=post.content
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.condition = form.condition.data
        post.img_url = form.img_url.data
        post.content = form.content.data

        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('make_post.html', form=form)


@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(Post, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = db.get_or_404(Post, post_id)
    comments = db.session.execute(db.select(Comment).where(Comment.post_id == post_id)).scalars()
    print(comments)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
            
        comment = Comment(text=form.text.data,
                          date=datetime.now().strftime("%B %d, %Y"),
                          author_name=current_user.name,
                          post_id=post.id)
        db.session.add(comment)
        db.session.commit()
    return render_template('post.html', post=post, comments=comments, form=form)


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Contact
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = f"""Subject: Sent from {request.form.get('name')}\n\n
Email:{request.form.get('email')} 
Phone Number:{request.form.get('phone')}

Message:{request.form.get('message')}"""

        with SMTP('smtp.gmail.com') as connection:
            connection.starttls()
            connection.login(MY_EMAIL, PASSWORD)
            connection.sendmail(
                from_addr=request.form.get('email'),
                to_addrs=MY_EMAIL,
                msg=message)
        return render_template('contact.html', msg_sent=True)
    return render_template('contact.html', msg_sent=False)


app.run(debug=True, port=10000)
