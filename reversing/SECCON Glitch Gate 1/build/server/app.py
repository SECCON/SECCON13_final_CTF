#!/usr/bin/env python3
import datetime
import flask
import sqlite3
import yaml
import os

app = flask.Flask(__name__)
app.secret_key = os.urandom(8).hex()

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

config['game']['day1']['start'] = datetime.datetime.strptime(
    config['game']['day1']['start'], '%Y/%m/%d %H:%M'
)
config['game']['day1']['end'] = datetime.datetime.strptime(
    config['game']['day1']['end'], '%Y/%m/%d %H:%M'
)
config['game']['day2']['start'] = datetime.datetime.strptime(
    config['game']['day2']['start'], '%Y/%m/%d %H:%M'
)
config['game']['day2']['end'] = datetime.datetime.strptime(
    config['game']['day2']['end'], '%Y/%m/%d %H:%M'
)
config['game']['stride'] = datetime.timedelta(minutes=config['game']['stride'])
config['game']['attempt'] = datetime.timedelta(minutes=config['game']['attempt'])
config['game']['day1']['n'] = (config['game']['day1']['end'] - config['game']['day1']['start']) // config['game']['stride']
config['game']['day2']['n'] = (config['game']['day2']['end'] - config['game']['day2']['start']) // config['game']['stride']
config['game']['n'] = max(config['game']['day1']['n'], config['game']['day2']['n'])


@app.route('/')
def home():
    sql = sqlite3.connect(config['server']['sql'])
    cur = sql.execute('SELECT name, day, idx FROM reservation')
    books = cur.fetchall()

    next_book = None
    next_time = None
    day_now = 1 if datetime.datetime.now() < config['game']['day1']['end'] else 2
    idx_now = (datetime.datetime.now() - config['game'][f'day{day_now}']['start']) // config['game']['stride']
    for name, day, index in books:
        if day == day_now and idx_now < index:
            next_book = name, day, index
            next_time = config['game'][f'day{day_now}']['start'] + config['game']['stride']*index
            break

    hour = datetime.timedelta(minutes=30)
    return flask.render_template('index.html',
                                 config=config, now=datetime.datetime.now(), books=books,
                                 hour=hour, next_book=next_book, next_time=next_time)

@app.route('/book', methods=['POST'])
def book():
    sql = sqlite3.connect(config['server']['sql'], isolation_level='IMMEDIATE')

    # トークンの検証
    token = flask.request.form.get('token')
    cur = sql.execute('SELECT name FROM teams WHERE token=?', (token,))
    row = cur.fetchone()
    if row is None:
        flask.flash("Invalid team token")
        return flask.redirect(flask.request.referrer or flask.url_for('home'))
    name = row[0]

    # 入力の検証
    day = int(flask.request.form.get('day', '0'))
    if day not in [1, 2]:
        flask.flash("Invalid day requested")
        return flask.redirect(flask.request.referrer or flask.url_for('home'))

    index = int(flask.request.form.get('index', '-1'))
    day1_max = (config['game']['day1']['end'] - config['game']['day1']['start']) // config['game']['stride']
    day2_max = (config['game']['day2']['end'] - config['game']['day2']['start']) // config['game']['stride']
    if index < 0 or \
         (day == 1 and index >= day1_max) or (day == 2 and index >= day2_max):
        flask.flash("Invalid time requested")
        return flask.redirect(flask.request.referrer or flask.url_for('home'))

    if day == 1:
        time = config['game']['day1']['start'] + config['game']['stride'] * index
    else:
        time = config['game']['day2']['start'] + config['game']['stride'] * index
    if datetime.datetime.now() - datetime.timedelta(hours=1) >= time:
        flask.flash("This slot has already ended")
        return flask.redirect(flask.request.referrer or flask.url_for('home'))

    # 予約の検証1: すでに取られてないか
    cur = sql.execute('SELECT * FROM reservation WHERE day=? AND idx=?', (day, index))
    row = cur.fetchone()
    if row is not None:
        flask.flash("This slot has already been taken")
        return flask.redirect(flask.request.referrer or flask.url_for('home'))

    # 予約の検証2: その日が予約済みでないか
    cur = sql.execute('SELECT * FROM reservation WHERE day=? AND name=?', (day, name))
    row = cur.fetchone()
    if row is not None:
        flask.flash(f"You have already reserved slot for Day {day}")
        return flask.redirect(flask.request.referrer or flask.url_for('home'))

    # 予約する
    try:
        sql.execute('INSERT INTO reservation(name, day, idx) VALUES(?, ?, ?)', (name, day, index))
        flask.flash("Successfully reserved slot")
    except Exception as e:
        flask.flash("Database error: Please try again")
        if sql: sql.rollback()
    finally:
        if sql: sql.commit()

    return flask.redirect(flask.request.referrer or flask.url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
