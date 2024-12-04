import datetime

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from flask_ckeditor import CKEditor


'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])  #CKE EDITOR Field
    author = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    submit_button = SubmitField(label='Publish')

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    if requested_post:
        print(requested_post)
        return render_template("post.html", post=requested_post)

# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=["GET", "POST"])
def new_post():
    blogForm = BlogForm()
    if blogForm.validate_on_submit():
        new_BlogPost = BlogPost(
            title=blogForm.title.data,
            subtitle=blogForm.subtitle.data,
            date=date.today().strftime("%B %d, %Y"),  # Format date for display
            body=blogForm.body.data,
            author=blogForm.author.data,
            img_url=blogForm.img_url.data,
        )
        db.session.add(new_BlogPost)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=blogForm, page_heading="New Post")


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    if requested_post:
        edit_form = BlogForm(
            title=requested_post.title,
            subtitle=requested_post.subtitle,
            img_url=requested_post.img_url,
            author=requested_post.author,
            body=requested_post.body
        )
        if edit_form.validate_on_submit():
            requested_post.title=edit_form.title.data
            requested_post.subtitle=edit_form.subtitle.data
            requested_post.date=requested_post.date
            requested_post.body=edit_form.body.data
            requested_post.author=edit_form.author.data
            requested_post.img_url=edit_form.img_url.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=requested_post.id))
        return render_template("make-post.html",form=edit_form, page_heading="Edit post", post=requested_post )

# TODO: delete_post() to remove a blog post from the database

@app.route("/delete/<post_id>")
def delete(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)