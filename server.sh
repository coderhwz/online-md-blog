#!/bin/sh
uwsgi --socket 127.0.0.1:3031 --wsgi-file app.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191 --daemonize /var/log/uwsgi.log