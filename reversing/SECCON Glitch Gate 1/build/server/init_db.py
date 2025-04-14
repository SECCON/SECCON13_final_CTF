#!/usr/bin/env python3
import os
import sqlite3
import yaml

with open("./config.yml") as f:
    config = yaml.safe_load(f)

if os.path.exists(config['server']['sql']):
    c = input("Are you sure you want to reset all team information? [y/N]")
    if c == 'y' or c == 'Y':
        os.unlink(config['server']['sql'])
    else:
        exit(1)

with sqlite3.connect(config['server']['sql']) as conn:
    cur = conn.cursor()
    # teams: チームID"id"のチーム名は"name"でトークンは"token"
    # reservation: 

    cur.executescript("""
CREATE TABLE teams(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name STRING UNIQUE,
  token STRING UNIQUE
);
CREATE TABLE reservation(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name STRING,
  day INTEGER,
  idx INTEGER
);
    """)

    if config['game']['is_dom']:
        teams = [[team['name'], team['team_token']] for team in config['teams']['dom']]
    else:
        teams = [[team['name'], team['team_token']] for team in config['teams']['int']]
    cur.executemany("INSERT INTO teams(name, token) VALUES(?, ?)", teams)
    conn.commit()

with sqlite3.connect('reservation.db') as conn:
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL")
    conn.commit()

print("[+] Done")
