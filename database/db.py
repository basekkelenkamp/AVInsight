import sqlite3


def get_db_connection():
    connection = sqlite3.connect("database/AVInsight.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Check if tables exist
    cursor.execute(
        """
    SELECT name FROM sqlite_master WHERE type='table' AND (name='metrics' OR name='metric_values');
    """
    )
    tables = cursor.fetchall()

    if len(tables) == 0:
        print("Attempting to create db tables..")

        q1 = """
            CREATE TABLE metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL)
            """

        q2 = """
            CREATE TABLE metric_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_id INTEGER NOT NULL,
            timestamp INT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (metric_id) REFERENCES metrics (id))
            """

        cursor.execute(q1)
        cursor.execute(q2)

        # Commit the table creation
        connection.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for x in cursor:
        print(x)

    # set to True to reset db
    clear_db = False
    if clear_db:
        cursor.execute("DROP TABLE IF EXISTS metrics")
        cursor.execute("DROP TABLE IF EXISTS metric_values")
        print("DROPPED TABLES")
        connection.commit()

    return connection


db = get_db_connection()
