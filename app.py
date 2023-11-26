from datetime import timezone
from flask import Flask, request, render_template, redirect, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import regex as re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pleasebekind'.encode('utf-16')


# if flase, if we quit browser the session is deleted
app.config["SESSION_PERMANENT"] = False
# stored in servers files and not the cookies
app.config["SESSION_TYPE"] = "filesystem"
# Activate session
Session(app)

# app config for database

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posty.db"
db = SQLAlchemy(app=app)

# Implement a database here and define the schemap

# for now in place of database, storing posts with the 
# required stuff in a global variable
POSTS = []
USERS = {}


@app.route("/")
def index():
    # default method is GET
    # need to check if we are logged into the session
    username = session.get("username")
    return render_template("index.html", username=username)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    # validates inputs and checks if login in is possible
    if request.method == "POST":

        # these checks below will not be necessary at all times
        # if an intruder tries editing the source file by removing the required filed, 
        # this code will make sure that there isnt a username or password with null value

        # check for username validity
        username = request.form.get("username")
        if " " in username:
            return render_template("error.html", message="Cant have spaces in a username")
        if not request.form.get("username"):
            return render_template("error.html", message="Invalid Username")
        password = request.form.get("password")
        if not request.form.get("password"):
            return render_template("error.html", message="Invalid Password")
        # check for password validity

        if username in USERS:
            if USERS[username] != password:
                return render_template("error.html", message="Invalid password")
        else:
            USERS[username] = password

        # here we add the homepage route, and before which add the username to session
        session["username"] = username
        session["password"] = password

        # all credentials satisfied so redirecting to /home
        return redirect("/home")
    # throw you back to / route if you arent signed in
    return "Signin Route"

@app.route("/logout")
def logout():
    # default method is get
    session.clear()
    session["username"] = ""
    # redirects back to home page once the 
    # session has been cleared
    return redirect('/')




# route to home page which has a view of all the posts
@app.route("/home")
def home():
    username = session.get("username")
    if not username:
        return redirect('/')
    return render_template("home.html", username=username, posts=POSTS[::-1])


# on clicking post button, we need to try to append the stuff into sql  
@app.route("/newpost", methods=["GET", "POST"])
def newpost():
    if request.method == "POST":
        post_id = len(POSTS) + 1
        username = session.get("username")
        post_content = request.form.get("post_content")
        time = datetime.utcnow()
        POSTS.append((post_id, username, post_content, time))
        return redirect('/home')

@app.route("/deletepost", methods=["GET", "POST"])
def deletepost():
    if request.method == "GET":
        post_id = request.args.get("post_id")
        for id_list in range(len(POSTS)):
            if str(post_id) == str(POSTS[id_list][0]):
                POSTS.pop(id_list)
                return redirect('/home')
        # return f"post id to be deleted {post_id}"