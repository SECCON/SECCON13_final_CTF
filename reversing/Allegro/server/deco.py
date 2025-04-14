import functools
import flask
import redis
import sqlite3

def redirect_authorized(url: str):
    """認証されたユーザーをリダイレクトする"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'id' in flask.session:
                return flask.redirect(flask.url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def redirect_unauthorized(url: str):
    """認証されていないユーザーをリダイレクトする"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'id' not in flask.session:
                return flask.redirect(flask.url_for(url, next=flask.request.endpoint))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def use_sql(db_path: str):
    """SQLite3を利用する"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'sql' not in flask.g:
                flask.g.sql = _get_sqlite_connection(db_path)
            return f(sql=flask.g.sql, *args, **kwargs)
        return decorated_function
    return decorator

def use_redis(redis_url: str):
    """Redisを利用する"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'redis' not in flask.g:
                flask.g.redis = _get_redis_connection(redis_url)
            return f(redis=flask.g.redis, *args, **kwargs)
        return decorated_function
    return decorator

def _get_sqlite_connection(db_path: str):
    return sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)

def _get_redis_connection(redis_url: str):
    return redis.Redis.from_url(redis_url)
