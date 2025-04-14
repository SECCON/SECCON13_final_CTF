import datetime
import json
import math
import os
import sqlite3
import yaml
from typing import List, Tuple, Union, Optional

def adapt_datetime(ts):
    """datetime 型を SQLite の TEXT 型に変換"""
    return ts.isoformat()

def convert_datetime(ts):
    """SQLite から取得した TEXT 型を datetime 型に変換"""
    return datetime.datetime.fromisoformat(ts.decode()) + \
        datetime.timedelta(hours=9) # FIXME: TODO: JST固定

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    config['server']['sql'] = os.path.realpath(config['server']['sql'])
    config['server']['phase'] = os.path.realpath(config['server']['phase'])
    config['server']['storage'] = os.path.realpath(config['server']['storage'])
    config['server']['logs'] = os.path.realpath(config['server']['logs'])

    config['game']['start'] = datetime.datetime.strptime(config['game']['start'], '%Y/%m/%d %H:%M')
    config['game']['end'] = datetime.datetime.strptime(config['game']['end'], '%Y/%m/%d %H:%M')
    config['game']['tick'] = datetime.timedelta(minutes=config['game']['tick'])
    check_time = 0
    for phase in config['game']['phase']:
        check_time += phase['span']
        phase['span'] = datetime.timedelta(minutes=phase['span'])

    config['game']['max_tick'] = config['game']['initial_tick'] + int((config['game']['end'] - config['game']['start']) / config['game']['tick']) - 1
    config['game']['max_phase'] = config['game']['initial_phase'] + len(config['game']['phase']) - 1

    assert config['game']['end'] > config['game']['start'], "Game: end >= start"
    assert (config['game']['end'] - config['game']['start']).total_seconds() // 60 == check_time, \
        "Game: end - start != sum(phase.span)"

    isolation = config['game']['isolation']
    isolation['cores_per_team'] = float(isolation.get('cores_per_team', -1))
    isolation['max_pids'] = int(isolation.get('max_pids', -1))
    isolation['memory'] = int(isolation.get('memory', -1))
    isolation['isolate_network'] = isolation.get('isolate_network', True)
    isolation['cap_add'] = isolation.get('cap_add', [])

    return config


def get_tick(config: dict) -> int:
    """現在のtickを取得する

    Returns:
      int: 現在のtick。ゲームが始まっていないときは0返す。ゲームが終わっているときは-1を返す。
    """
    now = datetime.datetime.now()
    if now < config['game']['start']:
        return 0
    elif now >= config['game']['end']:
        return -1
    else:
        return config['game']['initial_tick'] + int(
            (now - config['game']['start']) / config['game']['tick']
        )

def get_local_tick(config: dict, tick: int) -> int:
    """現在のローカルtickを取得する

    Returns:
      int: 現在のローカルtick。ゲームが始まっていないときは0返す。ゲームが終わっているときは-1を返す。
    """
    cur = config['game']['initial_tick']
    if tick < cur:
        return -1

    for phase in config['game']['phase']:
        if tick < cur + phase['span'] // config['game']['tick']:
            break
        cur += phase['span'] // config['game']['tick']
    else:
        return -1

    return tick - cur + 1

def get_phase(config: dict) -> int:
    """現在のphaseを取得する

    Returns:
      int: 現在のphase。ゲームが始まっていないときは0返す。ゲームが終わっているときは-1を返す。
    """
    now = datetime.datetime.now()
    if now < config['game']['start']:
        return 0
    elif now >= config['game']['end'] + config['game']['tick']:
        return -1

    phase_id = config['game']['initial_phase'] - 1
    cur = config['game']['start']
    for phase in config['game']['phase']:
        if now < cur:
            break
        phase_id += 1
        cur += phase['span']

    return phase_id

def get_phase_by_tick(config: dict, tick: int) -> int:
    """tick番号からphaseを取得する

    Returns:
      int: tickに対応するphase。ゲームが始まっていないときは0返す。ゲームが終わっているときは-1を返す。
    """
    if tick == 0:
        return 0
    elif tick == -1:
        return -1

    tick -= config['game']['initial_tick']
    if tick < 0:
        return 0

    phase_id = config['game']['initial_phase']
    cur = 0
    for phase in config['game']['phase']:
        if tick < cur + phase['span'] // config['game']['tick']:
            break
        phase_id += 1
        cur += phase['span'] // config['game']['tick']
    else:
        return -1

    return phase_id

def round_time(dt: datetime.datetime, delta: datetime.timedelta):
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = delta.seconds - (seconds % delta.seconds)
    return dt + datetime.timedelta(0, rounding, -dt.microsecond)

def get_next_tick_start(config: dict) -> datetime.datetime:
    """次のtickが始まる時刻を計算する

    Returns:
      datetime.datetime: 次のtickが始まる時刻。ゲームが終わっているときはゲーム終了時刻を返す。
    """
    now = datetime.datetime.now()
    if now < config['game']['start']:
        return config['game']['start']
    elif now >= config['game']['end']:
        return config['game']['end']

    return round_time(now, config['game']['tick'])


def get_teams(sql: sqlite3.Connection) -> List[Tuple[int, str]]:
    """チーム一覧を取得する
    """
    cur = sql.execute('SELECT id, name, token FROM teams ORDER BY id')
    return cur.fetchall()

def get_team_by_token(sql: sqlite3.Connection, token: str) -> Optional[Tuple[int, str]]:
    """トークンからチーム情報を取得する
    """
    cur = sql.execute('SELECT id, name FROM teams WHERE token = ?', (token,))
    return cur.fetchone()

def get_team_scores(sql: sqlite3.Connection) -> int:
    """全チームのスコアを取得する
    """
    cur = sql.execute('WITH latest_scoring AS (SELECT * FROM scoring WHERE id IN (SELECT MAX(id) FROM scoring GROUP BY team_id, tick)) SELECT team_id, SUM(score), RANK() OVER (ORDER BY SUM(score) DESC) FROM latest_scoring GROUP BY team_id ORDER BY team_id;') # TODO: 黒魔術
    return cur.fetchall()

def get_team_score(sql: sqlite3.Connection, team_id: int) -> int:
    """チームのスコアを取得する
    """
    cur = sql.execute('SELECT SUM(score) FROM scoring WHERE id IN (SELECT MAX(id) FROM scoring WHERE team_id = ? GROUP BY tick)', (team_id,))
    return cur.fetchone()

def set_teams_score(sql: sqlite3.Connection, scores: List[Tuple[int, int, int, int, str]]):
    """チームのスコアを挿入する

    phase, tickのスコアがすでに存在する場合も削除せずに追加する。
    """
    sql.executemany('INSERT INTO scoring (team_id, tick, phase, score, log) VALUES (?, ?, ?, ?, ?)', scores)
    sql.commit()

def get_history(sql: sqlite3.Connection) -> List[int]:
    """スコアのログを取得する
    """
    history = []

    cur = sql.execute('SELECT team_id, tick, phase, score, log FROM scoring')
    for team_id, tick, phase, score, log in cur.fetchall():
        if tick > len(history):
            history += [({}, phase) for _ in range(tick - len(history))]
        history[tick-1][0][team_id] = (score, json.loads(log))

    return history

def insert_storage(sql: sqlite3.Connection, team_id: int, phase: int, filename: str):
    """ストレージ情報を追加する
    """
    sql.execute('INSERT INTO storage (team_id, phase, filename) VALUES (?, ?, ?)',
                (team_id, phase, filename))
    sql.commit()

def get_uploads(sql: sqlite3.Connection, team_id: int):
    """チームの最後の投稿ファイルを取得する
    """
    cur = sql.execute('SELECT id, phase, timestamp FROM storage WHERE team_id = ? ORDER BY timestamp DESC', (team_id,))
    return cur.fetchall()

def get_upload_by_id(sql: sqlite3.Connection, team_id: int, file_id: int):
    """チームの最後の投稿ファイルを取得する
    """
    cur = sql.execute('SELECT phase, filename, timestamp FROM storage WHERE id = ? AND team_id = ?', (file_id, team_id))
    return cur.fetchone()

def get_latest_upload(sql: sqlite3.Connection, team_id: int, phase: int, by: datetime.datetime):
    """チームの最後の投稿ファイルを取得する
    """
    by -= datetime.timedelta(hours=9) # FIXME: TODO: JST固定
    cur = sql.execute('SELECT filename, timestamp FROM storage WHERE team_id = ? AND phase = ? AND timestamp < DATETIME(?) ORDER BY timestamp DESC LIMIT 1', (team_id, phase, by))
    return cur.fetchone()


if __name__ == '__main__':
    test_config = {
        'game': {
            'start': datetime.datetime(2024, 3, 1, 11, 0),
            'end': datetime.datetime(2024, 3, 1, 18, 0),
            'initial_phase': 1,
            'initial_tick': 1,
            'tick': datetime.timedelta(minutes=5),
            'phase': [
                {'span': datetime.timedelta(minutes=90)},
                {'span': datetime.timedelta(minutes=120)},
                {'span': datetime.timedelta(minutes=210)},
            ]
        },
    }

    # get_local_tick
    assert get_local_tick(test_config, 1) == 1
    assert get_local_tick(test_config, 18) == 18
    assert get_local_tick(test_config, 19) == 1
    assert get_local_tick(test_config, 25) == 7
    assert get_local_tick(test_config, 42) == 24
    assert get_local_tick(test_config, 43) == 1
    assert get_local_tick(test_config, 84) == 42
    assert get_local_tick(test_config, 85) == -1

    test_config['game']['initial_phase'] = 4
    test_config['game']['initial_tick'] = 85
    assert get_local_tick(test_config, 1) == -1
    assert get_local_tick(test_config, 85) == 1
    assert get_local_tick(test_config, 102) == 18
    assert get_local_tick(test_config, 103) == 1
    assert get_local_tick(test_config, 168) == 42
    assert get_local_tick(test_config, 169) == -1

    # get_phase_by_tick
    test_config['game']['initial_phase'] = 1
    test_config['game']['initial_tick'] = 1
    assert get_phase_by_tick(test_config, 0) == 0
    assert get_phase_by_tick(test_config, -1) == -1
    assert get_phase_by_tick(test_config, 1) == 1
    assert get_phase_by_tick(test_config, 18) == 1
    assert get_phase_by_tick(test_config, 19) == 2
    assert get_phase_by_tick(test_config, 25) == 2
    assert get_phase_by_tick(test_config, 42) == 2
    assert get_phase_by_tick(test_config, 43) == 3
    assert get_phase_by_tick(test_config, 84) == 3
    assert get_phase_by_tick(test_config, 85) == -1

    test_config['game']['initial_phase'] = 4
    test_config['game']['initial_tick'] = 85
    assert get_phase_by_tick(test_config, 1) == 0
    assert get_phase_by_tick(test_config, 85) == 4
    assert get_phase_by_tick(test_config, 102) == 4
    assert get_phase_by_tick(test_config, 103) == 5
    assert get_phase_by_tick(test_config, 168) == 6
    assert get_phase_by_tick(test_config, 169) == -1

    # get_tick / get_phase
    test_config['game']['initial_phase'] = 1
    test_config['game']['initial_tick'] = 1
    now = datetime.datetime.now()
    test_config['game']['start'] = now - datetime.timedelta(minutes=8)
    test_config['game']['end'] = now + datetime.timedelta(hours=6, minutes=52)
    assert get_tick(test_config) == 2
    assert get_phase(test_config) == 1

    test_config['game']['start'] = now - datetime.timedelta(minutes=90)
    test_config['game']['end'] = now + datetime.timedelta(hours=5, minutes=30)
    assert get_tick(test_config) == 19
    assert get_phase(test_config) == 2

    test_config['game']['start'] = now + datetime.timedelta(minutes=8)
    test_config['game']['end'] = now + datetime.timedelta(hours=7, minutes=8)
    assert get_tick(test_config) == 0
    assert get_phase(test_config) == 0

    test_config['game']['start'] = now - datetime.timedelta(hours=9)
    test_config['game']['end'] = now - datetime.timedelta(hours=2)
    assert get_tick(test_config) == -1
    assert get_phase(test_config) == -1

    test_config['game']['initial_phase'] = 4
    test_config['game']['initial_tick'] = 85
    now = datetime.datetime.now()
    test_config['game']['start'] = now - datetime.timedelta(minutes=8)
    test_config['game']['end'] = now + datetime.timedelta(hours=6, minutes=52)
    assert get_tick(test_config) == 86
    assert get_phase(test_config) == 4

    test_config['game']['start'] = now - datetime.timedelta(minutes=210)
    test_config['game']['end'] = now + datetime.timedelta(hours=3, minutes=30)
    assert get_tick(test_config) == 127
    assert get_phase(test_config) == 6

    test_config['game']['start'] = now + datetime.timedelta(minutes=8)
    test_config['game']['end'] = now + datetime.timedelta(hours=7, minutes=8)
    assert get_tick(test_config) == 0
    assert get_phase(test_config) == 0

    test_config['game']['start'] = now - datetime.timedelta(hours=9)
    test_config['game']['end'] = now - datetime.timedelta(hours=2)
    assert get_tick(test_config) == -1
    assert get_phase(test_config) == -1
