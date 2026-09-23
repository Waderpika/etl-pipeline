"""
Database layer for the Employee Transactions API.

Uses plain sqlite3 (no ORM) on purpose - this keeps the raw SQL visible,
which is the point of a project meant to demonstrate SQL/data-validation skills.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed_bad_data: bool = False):
    """Create tables and seed sample data.

    seed_bad_data=True intentionally inserts a couple of inconsistent rows
    (e.g. a transaction referencing a non-existent employee, a negative
    balance) so the reconciliation tests below have real defects to catch.
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL  -- 'credit' or 'debit'
        )
    """)

    # balance is intentionally set to equal sum(credits) - sum(debits) for
    # the corresponding transactions below, so the "clean" dataset reconciles.
    employees = [
        (1, "Asha Rao", "Engineering", 800),    # 1000 credit - 200 debit
        (2, "Vikram Shah", "Finance", 500),     # 500 credit
        (3, "Priya Nair", "Engineering", 700),  # 1000 credit - 300 debit
    ]
    cur.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", employees)

    transactions = [
        (1, 1, 1000, "credit"),
        (2, 1, 200, "debit"),
        (3, 2, 500, "credit"),
        (4, 3, 1000, "credit"),
        (5, 3, 300, "debit"),
    ]

    if seed_bad_data:
        # Defect 1: transaction references an employee that doesn't exist
        transactions.append((6, 99, 100, "credit"))
        # Defect 2: balance in employees table doesn't match sum of transactions
        cur.execute("UPDATE employees SET balance = 9999 WHERE id = 2")

    cur.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?)", transactions)

    conn.commit()
    conn.close()
