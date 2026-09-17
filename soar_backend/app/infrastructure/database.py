import os
import sqlite3
from app.core.config import settings

def init_db():
    db_dir = os.path.dirname(settings.DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  ip TEXT NOT NULL,
                  network TEXT,
                  description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rule_sources
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  url TEXT NOT NULL,
                  branch TEXT DEFAULT 'main',
                  rules_path TEXT,
                  description TEXT)''')

    # Инициализация тестовых сенсоров при первом запуске
    c.execute("SELECT COUNT(*) FROM sensors")
    if c.fetchone()[0] == 0:
        demo_sensors = [
            ("Sensor-Alpha", "10.8.0.2", "192.168.10.0/24", "DMZ Perimeter Sensor (Suricata NIDS + Zeek NTA)"),
            ("Sensor-Beta", "10.8.0.3", "192.168.20.0/24", "Internal Corporate Network Segment"),
            ("Sensor-Gamma", "10.8.0.4", "10.100.0.0/16", "Core Infrastructure & Data Center")
        ]
        c.executemany("INSERT INTO sensors (name, ip, network, description) VALUES (?, ?, ?, ?)", demo_sensors)

    # Инициализация базового источника правил
    c.execute("SELECT COUNT(*) FROM rule_sources")
    if c.fetchone()[0] == 0:
        demo_sources = [
            ("Emerging Threats Open Rules", "https://github.com/emerging-threats/rules", "master", "rules/emerging-all.rules", "Community Threat Intelligence feed for Suricata NIDS")
        ]
        c.executemany("INSERT INTO rule_sources (name, url, branch, rules_path, description) VALUES (?, ?, ?, ?, ?)", demo_sources)

    conn.commit()
    conn.close()

def get_db_connection():
    db_dir = os.path.dirname(settings.DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
