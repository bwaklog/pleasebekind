from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'pleasebekind'.encode('utf-16')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
db = SQLAlchemy(app)

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_user_handle = db.Column(db.Integer, nullable=False)
    post_content = db.Column(db.String(200), nullable=False)
    post_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

uid = ""
# Authentication Page
@app.route('/', methods=['POST', 'GET'])
def auth_signin():
    if request.method != "POST":
        return render_template('auth-signin.html')
    if len(request.form['user_handle']) > 1:
        uid = request.form['user_handle']
    else:
        flash("Username Missing 😔", category='message')
        return redirect('/')
    return redirect(f'home/{uid}')

@app.route('/signup/', methods=["POST", "GET"])
def auth_signup():
    if request.method == "POST":
        return redirect('/')
    else:
        return render_template('auth_signup.html')

# Home page
# This is where the content is going to be visiable
@app.route('/home/<uid>', methods=['POST', 'GET'])
def home(uid):
    if request.method == 'POST':
        if len(request.form['content']) > 1:
            post_content = request.form['content']
        else:
            flash("You can't have an empty post 😔", category='message')
            return redirect(f'/home/{uid}')
        new_post = Post(post_content=post_content, post_user_handle=uid)
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect(f'/home/{uid}')
        except Exception:
            return 'There was an issue sending the post'
    else:
        print("Rendering Home Page")
        posts = Post.query.order_by(Post.post_timestamp.desc()).all()
        return render_template('home.html', posts=posts, uid=uid)


if __name__ == "__main__":
    app.run(debug=True)
