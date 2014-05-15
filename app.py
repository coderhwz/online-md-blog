import os
import sqlite3
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
def hello():
    """@todo: Docstring for hello.
    :: @todo
    :returns: @todo

    """
    return 'hello world'

@app.route('/admin/posts')
def list_posts():
    """@todo: Docstring for list_posts.
    :returns: @todo

    """
    db = get_db()
    return render_template('admin/list_posts.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
