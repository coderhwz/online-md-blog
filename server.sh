uwsgi --socket 127.0.0.1:3031 --wsgi-file uwsgi.py --callable app  --stats 127.0.0.1:9191 --daemonize /var/log/uwsgi.log
# --processes 4 --threads 2
