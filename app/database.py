import sqlite3
from pathlib import Path


DB_PATH = Path("data/claims.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DB_PATH)


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            plan_status TEXT NOT NULL,
            enrollment_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            device TEXT NOT NULL,
            incident TEXT NOT NULL,
            damage TEXT NOT NULL,
            claim_status TEXT NOT NULL,
            FOREIGN KEY(customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    connection.commit()

    connection.close()


def seed_database():
    connection = get_connection()

    cursor = connection.cursor()

    customers = [
        (
            "C1001",
            "Rahul Sharma",
            "Premium",
            "ACTIVE",
            "2026-01-10",
        ),
        (
            "C1002",
            "Priya Singh",
            "Basic",
            "ACTIVE",
            "2026-02-15",
        ),
        (
            "C1003",
            "Amit Kumar",
            "Basic",
            "INACTIVE",
            "2026-03-01",
        ),
    ]

    claims = [
        (
            "CLM001",
            "C1001",
            "iPhone 15",
            "Accidental drop",
            "Cracked screen",
            "SUBMITTED",
        ),
        (
            "CLM002",
            "C1002",
            "Samsung Galaxy S24",
            "Accidental drop",
            "Minor scratches",
            "SUBMITTED",
        ),
        (
            "CLM003",
            "C1003",
            "Pixel 9",
            "Accidental drop",
            "Cracked screen",
            "SUBMITTED",
        ),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        VALUES (?, ?, ?, ?, ?)
    """, customers)

    cursor.executemany("""
        INSERT OR IGNORE INTO claims
        VALUES (?, ?, ?, ?, ?, ?)
    """, claims)

    connection.commit()

    connection.close()


if __name__ == "__main__":
    initialize_database()
    seed_database()

    print("Database initialized successfully.")