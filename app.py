import os
import sqlite3
import time
import markdown
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

@app.route('/<id>')
def post(id):
    """@todo: Docstring for post.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from posts where id=?',(id))
    post = cursor.fetchone()
    return render_template('post.html',post=post)

@app.route('/admin/posts')
def list_posts():
    """@todo: Docstring for list_posts.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from posts')
    posts = cursor.fetchall()
    return render_template('admin/post/list.html',posts=posts)

@app.route('/admin/post/edit',methods=['GET','POST'])
def post_edit():
    id = request.args.get('id',None)
    if not id:
        id = request.form.get('id',None) 
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        title = request.form.get('title')
        mdtext = request.form.get('markdown','')
        md = markdown.Markdown(extensions=['extra','codehilite','admonition','meta'])
        content = md.convert(mdtext)
        keyword = md.Meta.get('keyword',[""])[0]
        desc = md.Meta.get('description',[""])[0]
        if id:
            cursor.execute('select * from posts where id=%s' % (id))
            post = cursor.fetchone()
            if not post:
                return 'post not avaliable'
            else:
                cursor.execute('update posts set title=?,markdown=?,content=?,'+
                        'keyword=?,desc=?,update_at=? where id=?',
                        (title,mdtext,content,keyword,desc,time.time(),id))
                db.commit()
            return redirect(url_for('post_edit',id=id))

        else:

            cursor.execute('insert into posts values(null,?,?,?,?,?,?,?)',(title,
                markdown,content,str(keyword),desc,time.time(),time.time()))
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
    app.debug = True
    app.run()
