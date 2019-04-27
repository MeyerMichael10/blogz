from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'key'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title, body)
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
        
        return render_template('viewblog.html', blog_id=id, blog=blog)

    else:
        
        blogs = Blog.query.all()
        title = Blog.query.get('title')
        body = Blog.query.get('body')
        return render_template('blogs.html', blogs=blogs, title=title, body=body)










if __name__ == '__main__':
    app.run()
