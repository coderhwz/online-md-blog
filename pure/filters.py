import datetime

def timefmt(value,format="%Y-%m-%d"):
    return datetime.datetime.fromtimestamp(value).strftime(format)
