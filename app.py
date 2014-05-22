#--coding:utf-8--
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

def create_app():
    """创建一个新项目"""
    newApp = Flask(__name__)
    # newApp.config.from_object(__name__)

    newApp.jinja_env.filters['timefmt'] = filters.timefmt

    newApp.config.update(config)

    # newApp.config.from_envvar('FLASKR_SETTINGS',silent=True)
    return newApp 

app = create_app()

def connect_db():
    """连接数据库"""
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
    """
    获得数据库
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def requires_auth(f):
    """ 
    验证装饰器
    """
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
    """
    404 处理.
    """
    return render_template('404.html'),404

@app.route('/login',methods=['POST','GET'])
def login():
    """
    登录 
    """
    if request.method =='GET':
        return render_template('login.html')
    else:
        username = request.form.get('username',None)
        password = request.form.get('password',None)
        if not username or not password:
            return 'username || password need'

        if username != config['USERNAME']:
            return 'user name not match'

        # 需要utf8
        hashed = bcrypt.hashpw(password.encode('utf-8'),config['PASSWORD'])
        if  hashed == config['PASSWORD']:
            session['login'] = True
            return redirect(url_for('list_posts'))
        else:
            return 'auth error'


def get_stats():
    """@todo: Docstring for get_stats.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT count(*) from posts');
    posts_cnt = cursor.fetchone()
    cursor.execute('SELECT count(*) FROM posts WHERE status="publish"')
    pub_cnt = cursor.fetchone()
    cursor.execute('SELECT count(*) FROM tags')
    tags_cnt = cursor.fetchone()
    return {
            'posts_cnt':posts_cnt[0],
            'pub_cnt':pub_cnt[0],
            'tags_cnt':tags_cnt[0]
            }

    

@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts WHERE status="publish"')
    posts = cursor.fetchall()
    return render_template('home.html',posts=posts)

@app.route('/<slug>.html')
def show_post(slug):
    """@todo: Docstring for post.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts WHERE id=? OR slug=?',(slug,slug))
    post = cursor.fetchone()
    if post['status'] != 'publish' and not session['login']:
        abort(401)
    if not post:
        abort(404)
    return render_template('post.html',post=post)

@app.route('/tags')
def list_tags():
    """@todo: 标签页.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tags')
    tags = cursor.fetchall()
    return render_template('tags.html',tags=tags)

@app.route('/tag/<slug>')
def show_tag_posts(slug):
    """@todo: Docstring for show_tag.

    :arg1: @todo
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tags WHERE name="%s"' % (slug))
    tag = cursor.fetchone()
    if not tag:
        abort(404)

    cursor.execute('SELECT * FROM posts WHERE status = "publish" AND '\
            'id IN(SELECT post_id FROM rels WHERE tag_id=%s)'% (tag['id']))
    posts = cursor.fetchall()
    return render_template('tag-posts.html',posts=posts,tag=tag)


@app.route('/admin/posts')
@requires_auth
def list_posts():
    """@todo: Docstring for list_posts.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    stats = get_stats()
    return render_template('admin/post/list.html',posts=posts,stats=stats)


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
        md = markdown.Markdown(extensions=['extra','codehilite',
            'admonition','meta'])
        content = md.convert(mdtext)
        title = md.Meta.get('title',[""])[0].strip()
        keyword = md.Meta.get('keywords',[""])[0].strip()
        slug = md.Meta.get('slug',[""])[0].strip()

        desc = md.Meta.get('description',[""])[0].strip()
        status = md.Meta.get('status',[""])[0].strip()
        tags = md.Meta.get('tags',[""])[0].strip()
        status = md.Meta.get('status',[""])[0].strip()
        if id:
            cursor.execute('SELECT * FROM posts WHERE id=%s' % (id))
            post = cursor.fetchone()

            if slug != post['slug'] and slug_exists(slug):
                return "slug exists"
            if not post:
                abort(404)
            else:
                cursor.execute('UPDATE posts SET title=?,markdown=?,content=?,'+
                        'slug=?,keyword=?,desc=?,update_at=?,status=? where id=?',
                        (title,mdtext,content,slug,keyword,desc,time.time(),
                            status,id))
                ids = save_tags(tags)
                save_rels(ids,id)

                db.commit()
            return redirect(url_for('post_edit',id=id))

        else:
            if slug_exists(slug):
                return "slug exists"
            cursor.execute('INSERT INTO posts VALUES(null,?,?,?,?,?,?,?,?,?)',
                    (title, mdtext,content,slug,keyword,desc,status,
                        time.time(),time.time()))
            ids = save_tags(tags)
            save_rels(ids,cursor.lastrowid)
            db.commit()
            return redirect(url_for('post_edit',id=cursor.lastrowid))
    else:
        if id != None:
            cursor.execute('SELECT * FROM posts WHERE id=%s' % (id))
            post = cursor.fetchone()
        else:
            post = {}
            post['markdown']="title: \nkeyword:\ndescription: \ntags: \n"\
                    "slug: \nstatus: publish\n"
        return render_template('admin/post/edit.html',post=post)

def slug_exists(slug):
    """检查slug是否已经存在

    :slug: @todo
    :returns: @todo

    """
    slug = slug.strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts WHERE slug="%s"'%(slug))
    one = cursor.fetchone()
    return one



def save_tags(tags):
    """
    保存标签.
    """
    if len(tags) < 1:
        return 
    tags = tags.split('..')
    ids = []
    db = get_db()
    for tag in tags:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM tags WHERE name="%s"'%(tag))
        t = cursor.fetchone()
        if not t:
            cursor.execute('INSERT INTO tags VALUES(null,?,?)',
                    (tag,time.time()))
            ids.append(cursor.lastrowid)
        else:
            ids.append(t['id'])

    return ids

def save_rels(tag_ids,post_id):
    """
    保存标签关系.
    """
    if not tag_ids:
        return 
    db = get_db()
    for id in tag_ids:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM rels WHERE post_id=? AND tag_id=?',
                (post_id,id))
        row = cursor.fetchone()
        if not row:
            cursor.execute('INSERT INTO rels VALUES(NULL,?,?)',(
                id,post_id))



