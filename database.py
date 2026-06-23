import sqlite3
import json
from contextlib import contextmanager

DB_PATH = "mcpeasia.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            tier_channel_id INTEGER,
            tier_results_channel_id INTEGER,
            tier_staff_role_id INTEGER,
            tier_tester_role_id INTEGER,
            ticket_category_id INTEGER,
            tier_roles TEXT DEFAULT '{}'
        )
        """)
        try:
            cursor.execute("ALTER TABLE guild_config ADD COLUMN tier_roles TEXT DEFAULT '{}'")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE guild_config ADD COLUMN tier_message_id INTEGER")
        except sqlite3.OperationalError:
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tier_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            channel_id INTEGER,
            user_id INTEGER,
            gamemode TEXT NOT NULL,
            ign TEXT DEFAULT '',
            time TEXT DEFAULT '',
            status TEXT DEFAULT 'open',
            claimed_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        try:
            cursor.execute("ALTER TABLE tier_tickets ADD COLUMN ign TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE tier_tickets ADD COLUMN time TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tier_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            ign TEXT,
            previous_tier TEXT,
            new_tier TEXT,
            note TEXT,
            tester_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()

def get_guild_config(guild_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,)).fetchone()
        return dict(row) if row else None

def save_guild_config(guild_id: int, data: dict):
    with get_db() as conn:
        exists = conn.execute("SELECT 1 FROM guild_config WHERE guild_id = ?", (guild_id,)).fetchone()
        if exists:
            keys = list(data.keys())
            vals = [data[k] for k in keys]
            set_clause = ", ".join([f"{k} = ?" for k in keys])
            conn.execute(f"UPDATE guild_config SET {set_clause} WHERE guild_id = ?", vals + [guild_id])
        else:
            keys = ["guild_id"] + list(data.keys())
            vals = [guild_id] + [data[k] for k in data.keys()]
            placeholders = ", ".join(["?"] * len(keys))
            conn.execute(f"INSERT INTO guild_config ({', '.join(keys)}) VALUES ({placeholders})", vals)
        conn.commit()

def create_tier_ticket(guild_id: int, channel_id: int, user_id: int, gamemode: str, ign: str = "", time: str = ""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tier_tickets (guild_id, channel_id, user_id, gamemode, ign, time, status)
            VALUES (?, ?, ?, ?, ?, ?, 'open')
        """, (guild_id, channel_id, user_id, gamemode, ign, time))
        conn.commit()
        return cursor.lastrowid

def get_tier_ticket(channel_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tier_tickets WHERE channel_id = ?", (channel_id,)).fetchone()
        return dict(row) if row else None

def claim_tier_ticket(ticket_id: int, claimed_by: int):
    with get_db() as conn:
        conn.execute("UPDATE tier_tickets SET claimed_by = ?, status = 'claimed' WHERE id = ?", (claimed_by, ticket_id))
        conn.commit()

def close_tier_ticket(ticket_id: int):
    with get_db() as conn:
        conn.execute("UPDATE tier_tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
        conn.commit()

def save_tier_result(guild_id: int, user_id: int, ign: str, previous_tier: str, new_tier: str, note: str, tester_id: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO tier_results (guild_id, user_id, ign, previous_tier, new_tier, note, tester_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (guild_id, user_id, ign, previous_tier, new_tier, note, tester_id))
        conn.commit()

def get_tier_results(guild_id: int, limit: int = 10):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM tier_results WHERE guild_id = ? ORDER BY id DESC LIMIT ?", (guild_id, limit)).fetchall()
        return [dict(r) for r in rows]

def get_tier_role_mapping(guild_id: int):
    cfg = get_guild_config(guild_id)
    if cfg and cfg.get('tier_roles'):
        try:
            return json.loads(cfg['tier_roles'])
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}

def set_tier_role(guild_id: int, tier_name: str, role_id: int):
    mapping = get_tier_role_mapping(guild_id)
    mapping[tier_name] = role_id
    save_guild_config(guild_id, {"tier_roles": json.dumps(mapping)})

def remove_tier_role(guild_id: int, tier_name: str):
    mapping = get_tier_role_mapping(guild_id)
    mapping.pop(tier_name, None)
    save_guild_config(guild_id, {"tier_roles": json.dumps(mapping)})
