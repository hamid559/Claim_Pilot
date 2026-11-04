import sqlite3

from app.database import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("""
    SELECT
        c.claim_id,
        c.device,
        c.incident,
        c.damage,
        cu.name,
        cu.plan_type,
        cu.plan_status
    FROM claims c
    JOIN customers cu
        ON c.customer_id = cu.customer_id
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()