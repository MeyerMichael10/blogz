from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'key'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    
   

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return self.username

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(title, body, owner)
        if not title:
            flash("Don't forget to give your post a title!")
            return redirect('/newpost')
        if not body:
            flash("There's no content in that post!")
            return redirect('/newpost')
        db.session.add(new_post)
        db.session.commit()
        
        return redirect('/blog?id={0}'.format(new_post.id))


    return render_template('newpost.html')


@app.route('/blog',strict_slashes=False)
def view_blog():
   
    
    if 'id' in request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        user = Blog.query.get('owner_id')
        return render_template('viewblog.html', blog_id=id, blog=blog, user=user)

    if 'user' in request.args:
        user = request.args.get('user')
        posts = Blog.query.filter_by(owner_id=user).all()
        title = Blog.query.get('title')
        body = Blog.query.get('body')
        return render_template('blogs.html', posts=posts, title=title, body=body)
    
    else:
        
        users = User.query.all()
        posts = Blog.query.all()
        title = Blog.query.get('title')
        body = Blog.query.get('body')
        return render_template('blogs.html', users=users, posts=posts, title=title, body=body)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash("logged in")
                return redirect('/newpost')
            else:
                flash('Password is incorrect', 'error')
                print(user.pw_hash)
        else:
            flash('User does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            # TODO - better response message
            return '<h1>Duplicate user</h1>'
    return render_template('signup.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



if __name__ == '__main__':
    app.run()
