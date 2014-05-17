import os
import sqlite3
import time
import markdown
import datetime
import filters
import bcrypt
from config import config
from functools import wraps
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash,abort

app = Flask(__name__)
app.config.from_object(__name__)

app.jinja_env.filters['timefmt'] = filters.timefmt

app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'blog.db'),
    DEBUG=config.get('debug',False),
    SECRET_KEY=config['secret_key'],
    USERNAME=config['username'],
    PASSWORD=config['password'],
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

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if True != session.get('login',False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
@app.teardown_appcontext
def close_db(xx):
    """@todo: Docstring for close_db.

    :arg1: @todo
    :returns: @todo

    """
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close();

@app.errorhandler(404)
def page_not_found(e):
    """@todo: Docstring for page_not_found.

    :arg1: @todo
    :returns: @todo

    """
    return render_template('404.html'),404

@app.route('/login',methods=['POST','GET'])
def login():
    """@todo: Docstring for login.
    :returns: @todo

    """
    if request.method =='GET':
        return render_template('login.html')
    else:
        username = request.form.get('username',None)
        password = request.form.get('password',None)
        if not username or not password:
            return 'username || password need'

        if username != config['username']:
            return 'user name not match'

        if bcrypt.hashpw(password,config['password']) == config['password']:
            session['login'] = True
            return redirect(url_for('list_posts'))
        else:
            return 'auth error'



@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from posts')
    posts = cursor.fetchall()
    # posts = dict()
    return render_template('home.html',posts=posts)

@app.route('/<slug>.html')
def show_post(slug):
    """@todo: Docstring for post.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from posts where id=? OR slug=?',(slug,slug))
    post = cursor.fetchone()
    if not post:
        abort(404)
    return render_template('post.html',post=post)

@app.route('/admin/posts')
@requires_auth
def list_posts():
    """@todo: Docstring for list_posts.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from posts')
    posts = cursor.fetchall()
    return render_template('admin/post/list.html',posts=posts)


@app.route('/admin/settings')
@requires_auth
def settings():
    """@todo: Docstring for settings.
    :returns: @todo

    """
    return ''

@app.route('/admin/post/edit',methods=['GET','POST'])
@requires_auth
def post_edit():
    id = request.args.get('id',None)
    if not id:
        id = request.form.get('id',None) 
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        mdtext = request.form.get('markdown','')
        md = markdown.Markdown(extensions=['extra','codehilite','admonition','meta'])
        content = md.convert(mdtext)
        title = md.Meta.get('title',[""])[0].strip()
        keyword = md.Meta.get('keyword',[""])[0].strip()
        slug = md.Meta.get('slug',[""])[0].strip()
        desc = md.Meta.get('description',[""])[0].strip()
        if id:
            cursor.execute('select * from posts where id=%s' % (id))
            post = cursor.fetchone()
            if not post:
                abort(404)
            else:
                cursor.execute('update posts set title=?,markdown=?,content=?,'+
                        'slug=?,keyword=?,desc=?,update_at=? where id=?',
                        (title,mdtext,content,slug,keyword,desc,time.time(),id))
                db.commit()
            return redirect(url_for('post_edit',id=id))

        else:
            cursor.execute('insert into posts values(null,?,?,?,?,?,?,?,?)',(title,
                mdtext,content,slug,keyword,desc,time.time(),time.time()))
            db.commit()
            return redirect(url_for('post_edit',id=cursor.lastrowid))
    else:
        if id != None:
            cursor.execute('select * from posts where id=%s' % (id))
            post = cursor.fetchone()
        else:
            post = {}
        return render_template('admin/post/edit.html',post=post)



if __name__ == '__main__':
    app.run()
