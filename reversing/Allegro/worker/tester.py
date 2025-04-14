import json
import logging
import multiprocessing
import os
import shutil
import statistics
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple
from util import *

NUM_TEST_TRIAL = 20


logger = logging.getLogger()

def gen_test(config: Dict[str, Any], phase: int, local_tick: int) -> Optional[Dict[str, Any]]:
    """テストケースを作成する
    """
    logger.info(f" Creating test input...")
    test_path = os.path.join(config['server']['phase'], str(phase), 'tester/gen_test')

    for _ in range(3):
        try:
            p = subprocess.run([test_path, str(local_tick)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=30)
            if p.returncode != 0:
                logger.warning(f" Failed to generate test input:\n  {p.stderr.decode()}")
            else:
                return json.loads(p.stdout.decode())
        except Exception as e:
            logger.warning(f" Failed to generate test input:\n  {e}")

    else:
        # テストケースの生成に失敗
        logger.error(f" Giving up to generate test input... (FIX IT!!)")
        return None

def image_exists(name: str) -> bool:
    return name.encode() in subprocess.run([
        'docker', 'image', 'ls', '-f', f'reference={name}'
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout

def run_single_test(config, dirpath: str, testcase: Dict[str, Any]) -> Tuple[str, float, str]:
    """1回の実行を評価する
    """
    if not image_exists('koh-tester'):
        logger.error("Container 'koh-tester' not found")
        return ('system', 0.0, "Image not found: 'koh-tester'")

    isolation = config['game']['isolation']
    cores = isolation['cores_per_team']
    max_pids = isolation['max_pids']
    mem = isolation['memory']

    # docker起動オプションを設定
    name = os.urandom(4).hex()
    options = ['--rm', '--init', '-d', '--name', name, '-v', f'{dirpath}:/app:ro']
    if isolation['isolate_network']:
        options.append('--network=none')
    if isolation['cap_add']:
        if isinstance(isolation['cap_add'], list):
            options += [f'--cap-add={cap}' for cap in isolation['cap_add']]
        else:
            options.append(f'--cap-add={isolation["cap_add"]}')
    if isolation['cap_drop']:
        if isinstance(isolation['cap_drop'], list):
            options += [f'--cap-drop={cap}' for cap in isolation['cap_drop']]
        else:
            options.append(f'--cap-drop={isolation["cap_drop"]}')
    if mem > 0:
        options += ['-m', f'{mem}m']
    if max_pids > 0:
        options.append(f'--pids-limit={max_pids}')
    if cores > 0:
        options.append(f'--cpus={cores}')

    # 1. Dockerを起動
    # TODO: cpu-setcpusを指定
    p = subprocess.run(['docker', 'run'] + options + ['koh-tester'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if p.returncode != 0:
        logger.error("Error during `docker run`:")
        logger.error(p.stderr.strip().decode())
        return ('system', 0.0, "Could not run koh-tester")

    # 2. 実行時間を計測
    try:
        start = time.time()
        p = subprocess.Popen([
            'docker', 'exec', '-u', f'{os.getuid()}:{os.getgid()}', '-i', name, '/app/put', 
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o = p.communicate(bytes.fromhex(testcase['input']), timeout=3) # TIMEOUT
        elapsed = time.time() - start
        stdout, stderr = o[0].hex(), o[1].hex()
        returncode = p.returncode

    except subprocess.TimeoutExpired:
        return ('timeout', 0.0, "")

    finally:
        p.kill()

        # 3. コンテナを停止
        p = subprocess.run(['docker', 'stop', name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if p.returncode != 0:
            logger.warning(f"Could not stop container: {name}")

    if stdout == testcase['output']:
        return ('', elapsed, '')
    else:
        return ('wrong', 0.0, f'Exit code: {returncode}')


def run_team_test(config, id: int, tick: int, filepath: Optional[str], testcase: Dict[str, Any]):
    """1チームのテストケースを評価する
    """
    if filepath is None:
        # デフォルトの場合はタイムアウト
        return {'err': 'timeout'}

    os.chmod(filepath, 0o777)

    exec_times = []
    for _ in range(NUM_TEST_TRIAL):
        with tempfile.TemporaryDirectory() as td:
            os.chmod(td, 755)
            shutil.copy(filepath, os.path.join(td, 'put'))

            err, exec_time, detail = run_single_test(config, td, testcase)
            if err != '':
                return {'err': err, 'detail': detail}
            exec_times.append(exec_time)

    return {'err': 'ok', 'speed': round(statistics.median(exec_times), 1)}

def run_test(config,
             sql,
             tick: int,
             phase: int,
             teams: List[Tuple[int, str, str]],
             testcase: Dict[str, Any]) -> List[Any]:
    """テストケースを実行する
    """
    num_tasks = len(teams)
    results = []

    # tickに該当する時刻を計算
    testcase_time  = config['game']['start'] + config['game']['tick'] * (
        tick - config['game']['initial_tick']
    )

    with multiprocessing.Pool(processes=num_tasks) as pool:
        tasks = []

        for team_id, name, _ in teams:
            # 最新のファイルを取得
            row = get_latest_upload(sql, team_id, phase, testcase_time)
            if row is None:
                timestamp = 'N/A'
                filepath = None
            else:
                filename, timestamp = row
                filepath = os.path.join(config['server']['storage'], str(team_id), filename)
            logger.info(f"  Testing {name} with {filepath} (uploaded at {timestamp})")

            # ファイルをテスト
            task = pool.apply_async(run_team_test,
                                    args=(config, team_id, tick, filepath, testcase),
                                    error_callback=lambda e: None)
            tasks.append((team_id, name, task))

        # 結果を集計
        for team_id, name, task in tasks:
            try:
                result = task.get(timeout=NUM_TEST_TRIAL * 3 + 30)
                results.append([team_id, tick, phase, 0, result])
                logger.info(f" {name} => {result}")
            except multiprocessing.TimeoutError:
                logger.warning(f" {team_id}:{name} => Timeout")

    return results
