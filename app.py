from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
db = SQLAlchemy(app)

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_user_handle = db.Column(db.Integer, nullable=False)
    post_content = db.Column(db.String(200), nullable=False)
    post_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

uid = "hegde"
# Authentication Page
@app.route('/', methods=['POST', 'GET'])
def auth():
    if request.method == "GET":
        print("This is the auth page")
        time.sleep(2)
        return redirect(f'/home/{uid}')


# Home page
# This is where the content is going to be visiable
@app.route('/home/<uid>', methods=['POST', 'GET'])
def home(uid):
    if request.method == 'POST':
        post_content = request.form['content']
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
