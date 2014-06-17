#--coding:utf-8--
import os,sqlite3,time,datetime,markdown,bcrypt
from functools import wraps
from flask import request,session,g,redirect,url_for,abort,\
        render_template,flash,abort,make_response,jsonify
from pure import app


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

        if username != app.config['USERNAME']:
            return 'user name not match'

        # 需要utf8
        hashed = bcrypt.hashpw(password.encode('utf-8'),app.config['PASSWORD'])
        if  hashed == app.config['PASSWORD']:
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
    cursor.execute('SELECT COUNT(*) from posts');
    posts_cnt = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) FROM posts WHERE status="publish"')
    pub_cnt = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) FROM tags')
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
    cursor.execute('SELECT * FROM posts WHERE status="publish" ORDER BY'
            ' create_at DESC')
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
    if not post:
        abort(404);
    if post['status'] != 'publish' and not session.get('login',None):
        abort(401)
    if not post:
        abort(404)
    return render_template('post.html',post=post)

@app.route('/tag/<slug>')
def show_tag_posts(slug):
    """@todo: Docstring for show_tag.

    :arg1: @todo
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tags WHERE name=?' , (slug,))
    tag = cursor.fetchone()
    if not tag:
        abort(404)

    cursor.execute('SELECT * FROM posts WHERE status = "publish" AND '\
            'id IN(SELECT post_id FROM rels WHERE tag_id=?)', (tag['id'],))
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
    sql = 'SELECT * FROM posts';
    keyword = request.args.get('s','')
    if keyword:
        sql = sql+ ' WHERE title LIKE ?'  
    sql = sql + ' ORDER BY create_at DESC'
    if keyword:
        cursor.execute(sql,("%" + keyword +"%",))
    else:
        cursor.execute(sql)
    posts = cursor.fetchall()
    stats = get_stats()
    return render_template('admin/post/list.html',posts=posts,stats=stats,
            keyword=keyword)
@app.route('/admin/tags')
@requires_auth
def admin_list_tags():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT tags.name AS name,COUNT(rels.post_id) AS cnt FROM rels '
            'LEFT JOIN tags ON tags.id=rels.tag_id GROUP BY tags.id')
    tags = cursor.fetchall()
    return render_template('admin/tags.html',tags=tags)

@app.route('/tags')
def list_tags():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT tags.create_at,tags.name AS name,COUNT(rels.post_id) AS cnt FROM rels '
            'LEFT JOIN tags ON tags.id=rels.tag_id GROUP BY tags.id')
    tags = cursor.fetchall()
    return render_template('tags.html',tags=tags)

@app.route('/admin/post/delete/<int:id>')
@requires_auth
def delete_post(id):
    """@todo: Docstring for delete_posts.

    :arg1: @todo
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM posts WHERE id=?",(id,))
    cursor.execute("DELETE FROM rels WHERE post_id=?",(id,))
    db.commit()
    return redirect(url_for('list_posts'))


@app.route('/admin/settings')
@requires_auth
def settings():
    """@todo: Docstring for settings.
    :returns: @todo

    """
    return ''


@app.route('/admin/post/edit',methods=['GET','POST'])
@requires_auth
def edit_post():
    id = request.args.get('id',None)
    if not id:
        id = request.form.get('id',None) 
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        mdtext = request.form.get('markdown','')
        md = markdown.Markdown(extensions=['extra','fenced_code','codehilite',
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
            cursor.execute('SELECT * FROM posts WHERE id=?' , (id,))
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

            if request.headers.get('X-Requested-With',None) == 'XMLHttpRequest':
                return jsonify(code=200)
            return redirect(url_for('edit_post',id=id))

        else:
            if slug_exists(slug):
                return "slug exists"
            cursor.execute('INSERT INTO posts VALUES(null,?,?,?,?,?,?,?,?,?)',
                    (title, mdtext,content,slug,keyword,desc,status,
                        time.time(),time.time()))
            ids = save_tags(tags)
            save_rels(ids,cursor.lastrowid)
            db.commit()
            return redirect(url_for('edit_post',id=cursor.lastrowid))
    else:
        if id != None:
            cursor.execute('SELECT * FROM posts WHERE id=?' , (id,))
            post = cursor.fetchone()
        else:
            post = {}
            post['markdown']="title: \nkeyword: \ndescription: \ntags: \n"\
                    "slug: \nstatus: publish\n"
        return render_template('admin/post/edit.html',post=post)


@app.route('/feed')
def feed():
    """@todo: Docstring for feed.
    :returns: @todo

    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE status='publish'")
    posts = cursor.fetchall()
    response =  make_response(render_template('rss.xml',posts=posts))
    response.mimetype = 'text/xml'
    return response

def slug_exists(slug):
    """检查slug是否已经存在

    :slug: @todo
    :returns: @todo

    """
    slug = slug.strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts WHERE slug=?',(slug,))
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
        cursor.execute('SELECT * FROM tags WHERE lower(name)=lower(?)',(tag,))
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
    cursor = db.cursor()
    cursor.execute('DELETE FROM rels WHERE post_id=?', (post_id,))
    data = []
    for id in tag_ids:
        data.append((id,post_id))
    cursor.executemany('INSERT INTO rels VALUES(NULL,?,?)',(data))



