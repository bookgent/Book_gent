import sqlite3
from datetime import datetime

DB_NAME = "users.db"
PLAN_COSTS = {
    "Starter": 1.0,
    "Pro": 2.0,
    "Max": 3.5
}

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                credits REAL DEFAULT 3,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Schema migrations
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'credits' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN credits REAL DEFAULT 3")
        if 'books_count' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN books_count INTEGER DEFAULT 0")
        if 'cheatsheets_count' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN cheatsheets_count INTEGER DEFAULT 0")
        conn.commit()

def get_user_status(user_id):
    """Returns (credits, is_new)"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("INSERT INTO users (user_id, credits) VALUES (?, 3.0)", (user_id,))
            conn.commit()
            return 3.0, True
            
        return row[0], False

def get_credits(user_id):
    credits, _ = get_user_status(user_id)
    return credits

def deduct_credits(user_id, amount):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET credits = credits - ?, last_interaction = CURRENT_TIMESTAMP WHERE user_id = ?", (amount, user_id))
        conn.commit()

def has_enough_credits(user_id, plan="Starter"):
    cost = PLAN_COSTS.get(plan, 1.0)
    credits = get_credits(user_id)
    return credits >= cost

def increment_book_count(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET books_count = books_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()

def increment_cheatsheet_count(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET cheatsheets_count = cheatsheets_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()

def get_all_users():
    """Admin function: returns list of (user_id, credits, books, cheatsheets)"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, credits, books_count, cheatsheets_count FROM users")
        return cursor.fetchall()

def add_credits(user_id, amount):
    """Admin function: adds amount to user's credits"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Ensure user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (user_id, credits) VALUES (?, ?)", (user_id, amount))
        else:
            cursor.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()


# Initialize on import
init_db()
