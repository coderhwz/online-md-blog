# code:utf-8
import sys
import os
import fnmatch
import time
import sqlite3
reload(sys)
sys.setdefaultencoding('utf-8')

cx = sqlite3.connect('./blog.db')
cx.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
def save_to_db(title,markdown):
    """@todo: Docstring for save_to_db.

    :title: @todo
    :markdown: @todo
    :returns: @todo

    """
    cursor = cx.cursor()
    cursor.execute('insert into posts values(null,?,?,"","","","","",?,?)',
            (title,markdown,time.time(),time.time()))
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
                    content = content_file.read()
                content = content.replace(":date:","date:") \
                        .replace(":author:","author:") \
                        .replace(":slug:","slug:") \
                        .replace(":tags:","tags:") 
                content.encode('utf8')

                title = f.split('.')[0]
                save_to_db(title,content)
                # print(title)

if __name__ == '__main__':
    doit()
