import sqlite3
import pandas as pd
from datetime import date

DB_NAME = "expenses.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL,
            last_updated REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fixed_costs (
            name TEXT PRIMARY KEY,
            amount REAL,
            last_updated TEXT  -- <-- New column to track last update date (ISO format)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            type TEXT PRIMARY KEY,
            amount REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fixed_income (
            name TEXT PRIMARY KEY,
            amount REAL,
            last_updated TEXT  -- <-- Same here
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fund_history (
        name TEXT,
        fixed_amount REAL,
        actual_value REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    

def insert_expense(conn, date, description, category, amount):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, description, category, amount) VALUES (?, ?, ?, ?)",
                   (date, description, category, amount))
    conn.commit()

def get_expenses(conn):
    return pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)

def update_expense(conn, id, date, description, category, amount):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET date=?, description=?, category=?, amount=? WHERE id=?",
        (date, description, category, amount, id))
    conn.commit()

def delete_expense(conn, id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()

def upsert_fixed_cost(conn, name, amount):
    today = date.today().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fixed_costs (name, amount, last_updated) VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET amount=excluded.amount, last_updated=excluded.last_updated
    """, (name, amount, today))
    conn.commit()

def get_fixed_costs(conn):
    return pd.read_sql_query("SELECT name, amount, last_updated FROM fixed_costs", conn)

def delete_fixed_cost(conn, name):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fixed_costs WHERE name=?", (name,))
    conn.commit()

def upsert_fixed_income(conn, name, amount):
    today = date.today().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fixed_income (name, amount, last_updated) VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET amount=excluded.amount, last_updated=excluded.last_updated
    """, (name, amount, today))
    conn.commit()

def get_fixed_incomes(conn):
    return pd.read_sql_query("SELECT name, amount, last_updated FROM fixed_income", conn)

def delete_fixed_income(conn, name):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fixed_income WHERE name=?", (name,))
    conn.commit()

def get_income_dict(conn):
    df = pd.read_sql_query("SELECT * FROM income", conn)
    return df.set_index("type")["amount"].to_dict()

def get_all_fund_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM funds")
    return [row[0] for row in cursor.fetchall()]

def get_current_fixed_amount(conn, fund_name):
    cursor = conn.cursor()
    cursor.execute("SELECT fixed_amount FROM funds WHERE name = ?", (fund_name,))
    result = cursor.fetchone()
    return result[0] if result else 0.0

def update_fixed_amount(conn, fund_name, new_amount):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE funds
        SET fixed_amount = ?, last_updated = CURRENT_TIMESTAMP
        WHERE name = ?
    """, (new_amount, fund_name))
    conn.commit()

def insert_fund_entry(conn, name, fixed_amount, actual_value, timestamp=None):
    if not timestamp:
        timestamp = pd.Timestamp.now()

    # Convert to ISO string
    timestamp_str = timestamp.isoformat()

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fund_history (name, fixed_amount, actual_value, last_updated)
        VALUES (?, ?, ?, ?)
    """, (name, fixed_amount, actual_value, timestamp_str))
    conn.commit()

def get_fund_history(conn, name):
    return pd.read_sql_query(
        "SELECT * FROM fund_history WHERE name = ? ORDER BY last_updated",
        conn, params=(name,)
    )

def get_latest_fixed_amount(conn, name):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fixed_amount FROM fund_history
        WHERE name = ?
        ORDER BY last_updated DESC
        LIMIT 1
    """, (name,))
    row = cursor.fetchone()
    return row[0] if row else 0.0

def get_all_fund_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM fund_history")
    return [row[0] for row in cursor.fetchall()]
