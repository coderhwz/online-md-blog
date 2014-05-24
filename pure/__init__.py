#coding:utf8
from flask import Flask 
from pure import config as cfg
from pure import filters


def create_app():
    """创建一个新项目"""
    newApp = Flask(__name__)
    # newApp.config.from_object(__name__)

    newApp.jinja_env.filters['timefmt'] = filters.timefmt

    newApp.config.update(cfg.config)

    return newApp 

app = create_app()

from pure import views
