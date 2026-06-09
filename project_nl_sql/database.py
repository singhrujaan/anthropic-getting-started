# database.py
# 
# Creates a sample business database.
# Provides three functions the agent will use:
#
# 1. create_database() — builds tables and fills with data
# 2. get_schema()      — returns table/column info as text
# 3. execute_query()   — runs SQL and returns results safely

import sqlite3
import os

# Where the database file will be stored
DB_PATH = "project_nl_sql/business.db"


def create_database():
    """Creates tables and inserts sample data."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Table 1: Customers ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id  INTEGER PRIMARY KEY,
            name         TEXT,
            country      TEXT,
            joined_date  TEXT
        )
    """)

    # ── Table 2: Products ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id  INTEGER PRIMARY KEY,
            name        TEXT,
            category    TEXT,
            price       REAL,
            stock       INTEGER
        )
    """)

    # ── Table 3: Orders ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id     INTEGER PRIMARY KEY,
            customer_id  INTEGER,
            order_date   TEXT,
            total_amount REAL,
            status       TEXT
        )
    """)

    # ── Insert sample data ──
    customers = [
        (1, "Alice Johnson", "USA",       "2023-01-15"),
        (2, "Bob Smith",     "UK",        "2023-03-22"),
        (3, "Carol White",   "USA",       "2023-05-10"),
        (4, "David Brown",   "Canada",    "2023-07-01"),
        (5, "Eve Davis",     "Australia", "2023-09-14"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO customers VALUES (?,?,?,?)",
        customers
    )

    products = [
        (1, "Laptop Pro",     "Electronics", 1299.99, 50),
        (2, "Wireless Mouse", "Electronics",   29.99, 200),
        (3, "Desk Chair",     "Furniture",    299.99, 30),
        (4, "Notebook",       "Stationery",     4.99, 500),
        (5, "Monitor 4K",     "Electronics",  599.99, 25),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)",
        products
    )

    orders = [
        (1, 1, "2024-01-10", 1329.98, "completed"),
        (2, 2, "2024-01-15",  299.99, "completed"),
        (3, 3, "2024-02-01",  629.98, "completed"),
        (4, 1, "2024-02-14",  599.99, "shipped"),
        (5, 4, "2024-03-01", 1099.98, "completed"),
        (6, 5, "2024-03-15",   34.98, "pending"),
        (7, 2, "2024-04-01",  799.99, "completed"),
        (8, 3, "2024-04-20",   29.99, "shipped"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?)",
        orders
    )

    conn.commit()
    conn.close()
    print("Database created successfully")


def get_schema() -> str:
    """
    Reads the database and returns all table/column info
    as plain text that Claude can understand.

    Example output:
    Table: customers
      - customer_id: INTEGER (PRIMARY KEY)
      - name: TEXT
      - country: TEXT
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema_parts = []

    for (table_name,) in tables:

        # Get column details for this table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # Format each column as readable text
        col_lines = []
        for col in columns:
            col_id, col_name, col_type, not_null, default, is_pk = col
            pk = " (PRIMARY KEY)" if is_pk else ""
            col_lines.append(f"  - {col_name}: {col_type}{pk}")

        schema_parts.append(
            f"Table: {table_name}\n" + "\n".join(col_lines)
        )

    conn.close()
    return "\n\n".join(schema_parts)


def execute_query(sql: str) -> dict:
    """
    Runs a SQL query and returns results as a dictionary.

    Always returns:
    - success:   True or False
    - columns:   list of column names
    - rows:      list of result rows
    - row_count: number of rows returned
    - error:     error message if query failed
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(sql)

        # Get column names from the cursor
        columns = [desc[0] for desc in cursor.description] \
                  if cursor.description else []

        rows = cursor.fetchall()
        conn.close()

        return {
            "success":   True,
            "columns":   columns,
            "rows":      rows,
            "row_count": len(rows),
            "error":     None
        }

    except Exception as e:
        conn.close()
        return {
            "success":   False,
            "columns":   [],
            "rows":      [],
            "row_count": 0,
            "error":     str(e)
        }


# ── Test everything when run directly ──
if __name__ == "__main__":

    # Create the database
    create_database()

    # Show the schema
    print("\n=== DATABASE SCHEMA ===")
    print(get_schema())

    # Run a test query
    print("\n=== TEST QUERY ===")
    result = execute_query("SELECT * FROM customers")
    print(f"Columns: {result['columns']}")
    print(f"Rows returned: {result['row_count']}")
    for row in result['rows']:
        print(f"  {row}")