#!/usr/bin/env python3
import os
import sqlite3
import sys
from util import load_config

config = load_config('../config.yml')

if len(sys.argv) < 2:
    if config['game']['is_dom']:
        teams = config['teams']['dom']
    else:
        teams = config['teams']['int']

elif sys.argv[1].lower() == 'dom':
    teams = config['teams']['dom']

elif sys.argv[1].lower() == 'int':
    teams = config['teams']['int']

else:
    print(f"Usage: {sys.argv[0]} [dom|int]")
    exit(1)


if os.path.exists('teams.db'):
    c = input("Are you sure you want to reset all team information? [y/N]")
    if c == 'y' or c == 'Y':
        os.unlink('teams.db')
    else:
        exit(1)

with sqlite3.connect('teams.db') as conn:
    cur = conn.cursor()
    # teams: チームID"id"のチーム名は"name"でトークンは"token"
    # scoring: チームID"team_id"のチームが"tick/phase"に"score"点を獲得した（詳細情報は"log"）
    # storage: チームID"iteam_id"のチームが時刻"timestamp"にファイル"filename"をアップロードした

    cur.executescript("""
CREATE TABLE teams(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name STRING UNIQUE,
  token STRING UNIQUE
);
CREATE TABLE scoring(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  team_id INTEGER,
  tick INTEGER,
  phase INTEGER,
  score INTEGER,
  log STRING
);
CREATE TABLE storage(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  team_id INTEGER,
  phase INTEGER,
  filename STRING,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
    """)

    teams = [[team['name'], team['team_token']] for team in teams]
    cur.executemany("INSERT INTO teams(name, token) VALUES(?, ?)", teams)
    conn.commit()

with sqlite3.connect('teams.db') as conn:
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL")
    conn.commit()

print("[+] Done")
