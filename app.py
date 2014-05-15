import os
import sqlite3
import time
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'blog.db'),
    DEBUG=True,
    SECRET_KEY='dev',
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_envvar('FLASKR_SETTINGS',silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('blog.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(xx):
    """@todo: Docstring for close_db.

    :arg1: @todo
    :returns: @todo

    """
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close();

@app.route('/')
def home():
    """@todo: Docstring for home.

    :arg1: @todo
    :returns: @todo

    """
    return render_template('home.html')

@app.route('/<int:id>.html')
def post(id):
    """@todo: Docstring for post.
    :returns: @todo

    """
    return render_template('post.html')

@app.route('/admin/posts')
def list_posts():
    """@todo: Docstring for list_posts.
    :returns: @todo

    """
    db = get_db()
    return render_template('admin/post/list.html')

@app.route('/admin/post/edit',methods=["GET","POST"])
def post_edit(post_id=None):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute('insert into posts values(null,?,?,?,?)',(title,content,time.time(),time.time()))
        db.commit()
        return redirect(url_for('post_edit',id=cursor.lastrowid))
    else:
        id = request.args['id']
        cursor.execute('select * from posts where id=%s' % (id))
        post = cursor.fetchone()
        return render_template('admin/post/edit.html',post=post)


if __name__ == '__main__':
    app.debug = True
    app.run()
