# code:utf-8
import sys
import os
import fnmatch
import time
import sqlite3
import re
from datetime import datetime
import markdown
reload(sys)
sys.setdefaultencoding('utf-8')

cx = sqlite3.connect('./blog.db')
cx.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
def save_to_db(title,mdtext,slug,create_at):
    """@todo: Docstring for save_to_db.

    :title: @todo
    :markdown: @todo
    :returns: @todo

    """
    md = markdown.Markdown(extensions=['extra','codehilite',
        'admonition','meta'])
    content = md.convert(mdtext)
    cursor = cx.cursor()
    cursor.execute('insert into posts values(null,?,?,?,?,"","","",?,?)',
            (title,mdtext,content,slug,create_at,time.time()))
    cx.commit()


def doit():
    """@todo: Docstring for doit.
    :returns: @todo

    """
    rstPath = sys.argv[1]
    matches = []
    for root,dirnames,filenames in os.walk(rstPath):
        for f in filenames:
            if f[f.index('.'):] == '.rst':
                fullpath = os.path.abspath(os.path.join(root,f))
                with open(fullpath,'r') as content_file:
                    lines = content_file.readlines()

                title = lines[0]

                lines[0] = "title:" + lines[0]

                del lines[1]
                create_at = 0
                slug=""

                for line in lines:
                    m = re.findall("^:date: (.*)\n",line,re.DOTALL)
                    if m:
                        format = '%Y-%m-%d %H:%M'
                        if len(m[0]) < 11:
                            m[0] = m[0]+' 10:10'
                        create_at = time.mktime(datetime.strptime(m[0], format).timetuple())

                    ms = re.findall("^:slug: (.*)\n",line,re.DOTALL)
                    if ms:
                        slug = ms[0]

                content = "".join(lines)
                content = content.replace(":date:","date:") \
                        .replace(":author:","author:") \
                        .replace(":slug:","slug:") \
                        .replace(":category:","category:") \
                        .replace(":tags:","tags:") 
                content.encode('utf8')

                # print(content)
                # title = f.split('.')[0]
                save_to_db(title,content,slug,create_at)
                # print(title)

if __name__ == '__main__':
    doit()
