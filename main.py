from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm,RegistrationForm,LoginForm,CommentForm
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    # here author became a object and User-BlogPost have one-Many relationship
    auther_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")


    comments = relationship("Comment",back_populates="parent_post")

# TODO: Create a User table for all your registered users. 
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    name:Mapped[str] = mapped_column(String(250),nullable=False)
    email:Mapped[str] = mapped_column(String(250),nullable=False,unique=True)
    password:Mapped[str] = mapped_column(String(250),nullable=False)

    #posts = relationship("BlogPost") this line establishes the relation between User and BlogPost
    #back_populates refers to a property in BlogPost which reference back to Current Moder(User)
    #user and blogpost has one-many relationship
    posts = relationship("BlogPost",back_populates="author")

    # "comment_author" refers to the comment_author property in the Comment class.
    #user and comments has one-many relationship
    comments = relationship("Comment",back_populates="comment_author")

class Comment(db.Model):
    __tablename__="comments"

    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    text:Mapped[str]=mapped_column(Text,nullable=False)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(Integer,db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost",back_populates="comments")

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return db.get_or_404(User,id)

with app.app_context():
    db.create_all()

# with app.app_context():
#     new_user = User(
#         name="Jay",
#         email="admin@gmail.com",
#         password=generate_password_hash("2010",'pbkdf2',salt_length=16)
#     )
#     db.session.add(new_user)
#     db.session.commit()
'''Using @wraps(func) is a best practice when writing decorators because it ensures that the 
    decorated function retains its original identity and metadata like __name__ __doc__'''
def admin_only(func):
    @wraps(func)
    def wrapper_function(*args,**kwargs):
        if current_user.id==1:
            return func(*args,**kwargs)
        else:
            return abort(403)
    return wrapper_function
# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=["POST","GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = db.session.execute(db.select(User).where(User.email==form.email.data)).scalar()
        if existing_user:
            flash("you already registered with this email,login instead")
            return redirect(url_for('login'))
        form.password.data = generate_password_hash(form.password.data,'pbkdf2',salt_length=16)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password = form.password.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html",form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login',methods=["POST","GET"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        existing_user = db.session.execute(db.select(User).where(User.email==login_form.email.data)).scalar()
        if existing_user:
            if check_password_hash(existing_user.password,login_form.password.data):
                login_user(existing_user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("password is incorrect")
                return redirect(url_for('login'))
        else:
            flash("there exist no user with this email,register please")
            return redirect(url_for('login'))

    return render_template("login.html",form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    print(posts)
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>",methods=["POST","GET"])
def show_post(post_id):
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                text=comment_form.ckeditor.data,
                parent_post=db.get_or_404(BlogPost,post_id),
                comment_author=current_user,
            )
            db.session.add(new_comment)
            db.session.commit()
        else:
            flash('please login in order to comment')
            return redirect(url_for('login'))
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post,form=comment_form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
