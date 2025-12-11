# backend/db.py
import sqlite3
import json

def init_db(db_path="events.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        confidence REAL,
        bbox TEXT,
        timestamp INTEGER,
        source TEXT,
        meta TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_event(db_path, event_type, confidence, bbox, timestamp, source, meta):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO events (event_type, confidence, bbox, timestamp, source, meta) VALUES (?, ?, ?, ?, ?, ?)",
              (event_type, confidence, json.dumps(bbox), timestamp, source, json.dumps(meta)))
    event_id = c.lastrowid
    conn.commit()
    conn.close()
    return event_id

def get_recent_events(db_path, limit=50):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, event_type, confidence, bbox, timestamp, source, meta FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    events = []
    for r in rows:
        events.append({
            "id": r[0],
            "event_type": r[1],
            "confidence": r[2],
            "bbox": json.loads(r[3]),
            "timestamp": r[4],
            "source": r[5],
            "meta": json.loads(r[6])
        })
    return events
