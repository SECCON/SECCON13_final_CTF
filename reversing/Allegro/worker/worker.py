#!/usr/bin/env python3
import datetime
import json
import logging
import random
import requests
import sched
import sqlite3
import sys
import time
from typing import Dict
from scoring import *
from tester import *
from util import *

config = load_config("../config.yml")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s] %(asctime)s : %(message)s",
                              "%Y-%m-%d %H:%M:%S")
sh.setFormatter(formatter)
logger.addHandler(sh)


def send_score(tick: int, scores: Dict[str, str]):
    """スコアをスコアサーバに送信する
    """
    if config['game']['is_dom']:
        url = config['scoreboard']['dom_url']
        key = config['scoreboard']['dom_key']
    else:
        url = config['scoreboard']['int_url']
        key = config['scoreboard']['int_key']

    logger.info(f"Sending scores to {url}")
    logger.info(json.dumps(scores))

    data = {
        'category_name': config['scoreboard']['category_name'],
        'round': tick - config['game']['initial_tick'] + 1,
        'scores': scores,
        'override': True
    }

    res = requests.post(url,
                        headers={'Content-Type': 'application/json',
                                 'X-Api-Key': key},
                        data=json.dumps(data))
    logger.info(f"Status code: {res.status_code}")
    logger.info(f"Response: {res.text}")


def eval_tick(tick: int):
    """特定のtickを評価する
    """
    sql = sqlite3.connect(config['server']['sql'])
    local_tick = get_local_tick(config, tick)
    phase = get_phase_by_tick(config, tick)

    if local_tick == -1 or phase == -1:
        logger.warning(f"Aborting tick \033[1m(tick: {tick} / local_tick: {local_tick} / phase: {phase})\033[0m")
        return

    logger.info(f"Starting test \033[1m(tick: {tick} / local_tick: {local_tick} / phase: {phase})\033[0m")

    # テストケースを生成する
    logger.info(f" Generating testcase...")
    testcase = gen_test(config, phase, local_tick)
    if testcase is None:
        return
    with open(os.path.join(config['server']['logs'], f'{tick}-input.bin'), 'wb') as f:
        f.write(bytes.fromhex(testcase['input']))
    with open(os.path.join(config['server']['logs'], f'{tick}-output.bin'), 'wb') as f:
        f.write(bytes.fromhex(testcase['output']))

    # 全チームに対してテストを実行する
    teams = get_teams(sql)
    random.shuffle(teams)
    try:
        results = run_test(config, sql, tick, phase, teams, testcase)
    except Exception as e:
        logger.error(f" Giving up to run tests... (FIX IT!!)")
        logger.error(f" Error: {e}")
        return

    speeds = [sys.float_info.max for _ in range(len(results))]

    for i in range(len(results)):
        if 'speed' in results[i][4]:
            speeds[i] = results[i][4]['speed']
        results[i][4] = json.dumps(results[i][4])

    logger.info(f"Ending test (tick: {tick})")

    # スコアを付与
    points = distribute_score(config, speeds, bigger_is_better=False)
    for i in range(len(points)):
        results[i][3] = points[i]
    set_teams_score(sql, results)

    # スコアサーバに送信
    token_by_id = {}
    for team_id, _, token in get_teams(sql):
        token_by_id[team_id] = token

    scores = []
    for team_id, _, _, score, _ in results:
        scores.append({'team_token': token_by_id[team_id], 'point': score})

    try:
        send_score(tick, scores)
    except Exception as e:
        logger.error(f"Could not send score: {e}")


def scheduled_worker(s: sched.scheduler):
    if datetime.datetime.now() >= config['game']['end']:
        logger.info("CTF is over!")
        return

    # 次のtickのテストを予約する
    if datetime.datetime.now() < config['game']['end']:
        next_start = get_next_tick_start(config)
        delta = (next_start - datetime.datetime.now()).total_seconds()
        logger.info(f"Next tick scheduled at {next_start} ({delta} seconds later)")
        s.enter(delta, 1, scheduled_worker, argument=(s,))

    tick = get_tick(config)
    phase = get_phase(config)
    eval_tick(tick)


if __name__ == '__main__':
    s = sched.scheduler(time.time, time.sleep)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'now':
            next_start = datetime.datetime.now()
            delta = 0
        else:
            tick = int(sys.argv[1])

            yn = input(f"Are you sure you want to recalculate tick={tick}? [y/N] ")
            if yn != 'y' and yn != 'Y':
                exit(1)

            clk = config['game']['start'] + config['game']['tick'] * (
                tick - config['game']['initial_tick']
            )
            logger.info(f"Recalculating tick={tick}... (Clock: {clk})")
            eval_tick(tick)
            exit(0)

    else:
        next_start = get_next_tick_start(config)

    delta = (next_start - datetime.datetime.now()).total_seconds()
    logger.info(f"Next tick scheduled at {next_start} ({delta} seconds later)")
    s.enter(delta, 1, scheduled_worker, argument=(s,))
    s.run()
