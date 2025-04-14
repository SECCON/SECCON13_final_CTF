#!/usr/bin/env python3
import base64
import datetime
import flask
import hashlib
import os
import subprocess
from deco import *
from util import *

config = load_config("../config.yml")

app = flask.Flask(__name__)
app.secret_key = config['server']['secret_key'].encode()
app.config['MAX_CONTENT_LENGTH'] = 50 * 1000 * 1000 # TODO: dynamic?

app.jinja_env.globals.update(get_tick=get_tick)
app.jinja_env.globals.update(get_phase=get_phase)
app.jinja_env.globals.update(get_phase_by_tick=get_phase_by_tick)

if app.secret_key == b"test":
    print("*****************************")
    print("*** Running in test mode! ***")
    print("*****************************")

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')

"""
ブラウザに表示させるページまわり
"""
@app.route('/', methods=['GET', 'POST'])
@use_sql(config['server']['sql'])
@redirect_authorized('dashboard')
def login(sql):
    if flask.request.method == 'POST':
        token = flask.request.form.get('token', '')
        row = get_team_by_token(sql, token)
        if row is None:
            flask.flash("Invalid team token")
        else:
            flask.session['id'], flask.session['name'] = row
            endpoint = flask.request.args.get('next') or 'dashboard'
            return flask.redirect(flask.url_for(endpoint))

    return flask.render_template("login.html", config=config)

@app.route('/dashboard', methods=['GET'])
@use_sql(config['server']['sql'])
@redirect_unauthorized('login')
def dashboard(sql):
    hashval, timestamp = '(Not uploaded yet)', config['game']['start']

    row = get_latest_upload(sql, flask.session['id'], get_phase(config), datetime.datetime.now())
    if row is not None:
        filename, timestamp = row
        directory = os.path.join(config['server']['storage'], str(flask.session['id']))

        sha256 = hashlib.sha256()
        with open(os.path.join(directory, filename), 'rb') as f:
            for chunk in iter(lambda: f.read(1000*1000), b''):
                sha256.update(chunk)
        hashval = sha256.hexdigest()

    return flask.render_template('dashboard.html',
                                 config=config, sha256=hashval, timestamp=timestamp)

@app.route('/scoreboard', methods=['GET'])
@use_sql(config['server']['sql'])
@redirect_unauthorized('login')
def scoreboard(sql):
    teams = list(map(lambda x: (x[0], x[1]), get_teams(sql)))
    scores = get_team_scores(sql)
    history = get_history(sql)
    if len(scores) == 0:
        scores = [(id, 0, 1) for id, name, _ in teams]

    phases = []
    prev_phase, prev_tick = 1, 0
    for tick, ( _, phase) in enumerate(history):
        # TODO: phaseをスキップして評価するとscoreboardのphase欄が壊れる
        if phase != prev_phase:
            phases.append((prev_phase, tick - prev_tick))
            prev_phase = phase
            prev_tick = tick
    phases.append((prev_phase, len(history) - prev_tick))
    phases.reverse()

    return flask.render_template('scoreboard.html',
                                 config=config, history=history, teams=teams, scores=scores, phases=phases)

@app.route('/history', methods=['GET'])
@use_sql(config['server']['sql'])
@redirect_unauthorized('login')
def history(sql):
    storage = get_uploads(sql, flask.session['id'])
    return flask.render_template('history.html', config=config, storage=storage)

@app.route('/rule', methods=['GET'])
def rule():
    lscpu = subprocess.check_output(["lscpu"]).decode()
    return flask.render_template('rule.html', config=config, lscpu=lscpu)

@app.route('/challenge', methods=['GET'])
@redirect_unauthorized('login')
def api_challenge():
    phase = get_phase(config)
    if phase == -1:
        return flask.abort(404, 'Game is over')

    directory = os.path.join(config['server']['phase'], str(phase))
    return flask.send_file(os.path.join(directory, 'files.tar.gz'),
                           download_name=f'prog-{phase}.tar.gz',
                           mimetype='application/octet-stream')

# TODO: Playground追加
@app.route('/playground', methods=['GET'])
@redirect_unauthorized('login')
def playground():
    pass

"""
# TODO: テストケースログ追加 → ファイルが重いので削除
@app.route('/testcase', methods=['GET'])
@redirect_unauthorized('login')
def testcase():
    return flask.render_template('testcase.html', config=config)

@app.route('/api/testcase/<int:tick>', methods=['GET'])
@redirect_unauthorized('login')
def api_testcase_tick(tick: int):
    i_path = os.path.join(config['server']['logs'], f'{tick}-input.bin')
    o_path = os.path.join(config['server']['logs'], f'{tick}-output.bin')
    if not os.path.exists(i_path) or not os.path.exists(o_path):
        if 'id' in flask.session:
            return flask.abort(404, "Invalid file ID")
        else:
            return {'message': 'Invalid file ID'}, 401

    testcase = {}
    with open(i_path, 'rb') as f:
        testcase['input'] = f.read().hex()
    with open(o_path, 'rb') as f:
        testcase['output'] = f.read().hex()

    if 'id' in flask.session:
        # ブラウザモード
        return flask.render_template("testcase_view.html", config=config, testcase=testcase)

    else:
        # APIモード
        return {'messaage': 'OK', 'testcase': testcase}
"""

"""
ユーザーがアップロードしたファイルが残るストレージまわり
"""
@app.route('/api/storage/<int:file_id>', methods=['GET'])
@use_sql(config['server']['sql'])
@redirect_unauthorized('login')
def api_storage_id(file_id: int, sql):
    if 'id' in flask.session:
        # ブラウザモード
        row = get_upload_by_id(sql, flask.session['id'], file_id)
        if row is None:
            return flask.abort(404, "Invalid file ID")
        filename = row[1]

        directory = os.path.join(config['server']['storage'], str(flask.session['id']))
        return flask.send_file(os.path.join(directory, filename),
                               download_name=filename,
                               mimetype='application/octet-stream')

    else:
        # APIモード
        token = flask.request.headers.get('x-token', '')
        row = get_team_by_token(sql, token)
        if row is None:
            return {'message': 'Invalid team token'}, 401
        team_id = row[0]

        row = get_upload_by_id(sql, team_id, file_id)
        if row is None:
            return {'message': 'Invalid file ID'}, 404
        filename = row[1]

        directory = os.path.join(config['server']['storage'], str(team_id))
        try:
            with open(os.path.join(directory, filename), 'rb') as f:
                b64bin = base64.b64encode(f.read()).decode()
            return {'message': 'OK', 'binary': b64bin}

        except Exception as e:
            print("[ERROR]", e)
            return {'message': 'Internal server error'}, 500


"""
その他APIまわり
"""
@app.route('/api/upload', methods=['POST'])
@use_sql(config['server']['sql'])
def api_upload(sql):
    phase = get_phase(config)
    # TODO: フェーズの切り替わりでは1 tickだけアップロードを禁止する

    if 'id' in flask.session:
        # ブラウザモード
        if phase == 0:
            return flask.abort(404, 'Game is not started')
        elif phase == -1:
            return flask.abort(404, 'Game is over')

        team_id, teamname = flask.session['id'], flask.session['name']
        file = flask.request.files.get('file')
        if not file:
            return flask.abort(400, 'Empty file')

    else:
        if phase == 0:
            return {'message': 'Game is not started'}, 404
        elif phase == -1:
            return {'message': 'Game is over'}, 404

        token = flask.request.headers.get('x-token', '')
        row = get_team_by_token(sql, token)
        if row is None:
            return {'message': 'Invalid team token'}, 401

        team_id, teamname = row
        file = flask.request.files.get('file')
        if not file:
            return {'message': 'Empty file'}, 400

    # ファイル保存 ("<storage path>/<team id>/<datetime>_<random>.bin")
    directory = os.path.join(config['server']['storage'], str(team_id))
    os.makedirs(directory, exist_ok=True)
    filename = f"{datetime.datetime.now().strftime('%m%d-%H%M%S')}_{os.urandom(4).hex()}.bin"
    file.save(os.path.join(directory, filename))

    # 誤アップロード防止
    file.stream.seek(0)
    if file.stream.read(4) != b'\x7fELF':
        if 'id' in flask.session:
            # フロントエンドで防止されているが、一応エラー表示する
            flask.flash("Invalid file format. Upload a valid ELF file. [*** WARNING ***]")
            return flask.redirect(flask.url_for('dashboard'))
        else:
            return {'message': 'Invalid file format. Upload a valid ELF file.'}, 400

    sha256 = hashlib.sha256()
    file.stream.seek(0)
    for chunk in iter(lambda: file.stream.read(1000*1000), b''):
        sha256.update(chunk)

    # DBに記録
    insert_storage(sql, team_id, phase, filename)

    if 'id' in flask.session:
        flask.flash("Your program is successfully uploaded")
        return flask.redirect(flask.url_for('dashboard'))
    else:
        return {'message': 'OK', 'info': {'sha256': sha256.hexdigest(), 'team': teamname}}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)
