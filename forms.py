from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

categories = [('Food', 'Food'), ('Baby', 'Baby'), ('Clothes', 'Clothes'), ('Furniture', 'Furniture'),
              ('Electronics', 'Electronics'), ('Sports and Outdoors', 'Sports and Outdoors'),
              ('Toys', 'Toys'),  ('Beauty and Personal Care', 'Beauty and Personal Care'), ('Other', 'Other')]

areas = [('Tel Aviv-Yafo', 'Tel Aviv-Yafo'), ('Jerusalem', 'Jerusalem'), ('Haifa', 'Haifa'),
         ('Sea of Galilee', 'Sea of Galilee'), ('Galilee', 'Galilee'), ('Golan', 'Golan'),
         ('Negev', 'Negev'), ('Arava', 'Arava')]

conditions = [('New', 'New'), ('Used', 'Used')]


class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    category = SelectField("Category", choices=categories)
    condition = SelectField("Condition", choices=conditions)
    img_url = URLField("Image URL", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("SUBMIT POST")


class RegisterForm(FlaskForm):
    name = StringField("User Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    area = SelectField("Area", choices=areas)
    address = StringField("Address", validators=[DataRequired()])
    address_url = URLField("Address URL", validators=[DataRequired()])
    submit = SubmitField("SUBMIT!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("SUBMIT")


class SearchForm(FlaskForm):
    category = SelectField("Category", choices=categories)
    area = SelectField("Area", choices=areas)
    submit = SubmitField("🔍")


class CommentForm(FlaskForm):
    text = CKEditorField(name="Comment")
    submit = SubmitField("POST")

