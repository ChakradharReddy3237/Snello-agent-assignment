import sqlite3

def initialize_database(db_name="todo.db"):
    """Initializes the database and creates the 'todos' table if it doesn't exist."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_item(item, db_name="todo.db"):
    """Adds a new item to the to-do list."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (item) VALUES (?)", (item,))
    conn.commit()
    conn.close()

def remove_item(item_id, db_name="todo.db"):
    """Removes an item from the to-do list based on its ID.
    
    Returns:
        bool: True if an item was deleted, False otherwise.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (item_id,))
    
    # Check how many rows were affected. If > 0, the deletion was successful.
    rows_affected = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_affected > 0

def list_items(db_name="todo.db"):
    """Lists all items in the to-do list."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, item FROM todos")
    items = cursor.fetchall()
    conn.close()
    return items

def clear_all_todos(db_name="todo.db"):
    """Deletes all items from the todos table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # DELETE without a WHERE clause removes all rows
    cursor.execute("DELETE FROM todos")
    # Optional: Reset the autoincrement counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='todos'")
    conn.commit()
    conn.close()
    print("--- All to-do items have been cleared. ---")