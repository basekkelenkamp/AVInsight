import pytest
import sqlite3
import json
from datetime import datetime, timedelta
import pytz
import zlib
from database.db import (
    db_get_all_metrics,
    db_get_metric_values_from_day,
    db_init_connection,
    insert_metric,
    insert_metric_value,
    remove_archive_after_days,
    save_data_report,
)


@pytest.fixture
def db_cursor():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    cursor = connection.cursor()

    # Check if tables exist
    cursor.execute(
        """
        SELECT name FROM sqlite_master WHERE type='table' AND (name='metrics' OR name='metric_values' OR name='daily_reports');
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
            timestamp TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (metric_id) REFERENCES metrics (id))
            """

        q3 = """
            CREATE TABLE daily_reports (
            date_id TEXT PRIMARY KEY,
            report_finished BOOLEAN,
            first_timestamp TEXT,
            last_timestamp TEXT,
            daily_counts TEXT,
            daily_max TEXT,
            daily_avg TEXT,
            thresholds TEXT,
            total_points_count INTEGER,
            minute_data BLOB)
            """

        cursor.execute(q1)
        cursor.execute(q2)
        cursor.execute(q3)

        metrics = ["CPU", "GPU", "RAM", "DISK"]

        for metric in metrics:
            insert_metric(cursor, metric)

        connection.commit()

    yield cursor
    connection.close()


def test_insert_metric(db_cursor):
    metric_type = "CPU"
    id = insert_metric(db_cursor, metric_type)
    db_cursor.execute("SELECT * FROM metrics WHERE id=?", (id,))
    result = db_cursor.fetchone()
    assert result is not None
    assert result["type"] == metric_type


def test_insert_metric_value(db_cursor):
    metric_type = "CPU"
    metric_id = insert_metric(db_cursor, metric_type)
    value = {"test_usage": 70}
    insert_metric_value(db_cursor, metric_id, value)

    db_cursor.execute("SELECT * FROM metric_values WHERE metric_id=?", (metric_id,))
    result = db_cursor.fetchone()

    assert result is not None
    assert json.loads(result["value"]) == value


def test_db_get_all_metrics(db_cursor):
    metric_types = ["CPU", "GPU", "RAM", "DISK"]
    metrics = db_get_all_metrics(db_cursor)

    assert len(metrics) == len(metric_types)
    for metric in metrics:
        assert metric["type"] in metric_types


def test_db_get_metric_values_from_day(db_cursor):
    metric_id = insert_metric(db_cursor, "TEST_METRIC")

    # Test data
    metric_values = [
        {"usage": 20, "timestamp": "2023-01-01 10:30:00.000"},
        {"usage": 50, "timestamp": "2023-01-01 12:00:00.000"},
        {"usage": 80, "timestamp": "2023-01-01 15:45:00.000"},
        # Adding a value from another day
        {"usage": 30, "timestamp": "2023-01-02 11:00:00.000"},
    ]

    for value in metric_values:
        query_insert_metric_value = """
            INSERT INTO metric_values (metric_id, value, timestamp) VALUES (?, ?, ?)
            """
        db_cursor.execute(
            query_insert_metric_value,
            (metric_id, json.dumps(value["usage"]), value["timestamp"]),
        )

    db_cursor.connection.commit()

    metric_values, day, prev_date, next_date = db_get_metric_values_from_day(
        db_cursor, "2023-01-01"
    )

    assert len(metric_values) == 3
    for value in metric_values:
        assert value["timestamp"].startswith("2023-01-01")
    assert day == "2023-01-01"
    assert prev_date == "2022-12-31"
    assert next_date == "2023-01-02"


def test_remove_archive_after_days(db_cursor):
    metric_id = insert_metric(db_cursor, "CPU")
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    now_timestamp = (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
    # Test data
    metric_values = [
        {"usage": 20, "timestamp": "2023-01-01 10:30:00.000"},
        {"usage": 50, "timestamp": "2023-01-02 12:00:00.000"},
        {"usage": 80, "timestamp": "2023-01-03 15:45:00.000"},
        {"usage": 30, "timestamp": now_timestamp},
    ]

    for value in metric_values:
        query_insert_metric_value = """
            INSERT INTO metric_values (metric_id, value, timestamp) VALUES (?, ?, ?)
            """
        db_cursor.execute(
            query_insert_metric_value,
            (metric_id, json.dumps(value["usage"]), value["timestamp"]),
        )

    # Insert daily reports for the same days
    for i in range(5):
        date_id = f"2023-01-0{i+1}"
        query_insert_daily_report = """
            INSERT INTO daily_reports (date_id, report_finished, first_timestamp, last_timestamp, daily_counts, daily_max, daily_avg, thresholds, total_points_count, minute_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        db_cursor.execute(
            query_insert_daily_report,
            (
                date_id,
                1,
                f"{date_id} 00:00:00.000",
                f"{date_id} 23:59:59.999",
                "{'CPU': 100}",
                "{'CPU': 80}",
                "{'CPU': 40}",
                "{'CPU': 70}",
                100,
                zlib.compress(bytes(json.dumps([]), "utf-8")),
            ),
        )

    db_cursor.connection.commit()

    # Remove metric values and daily reports older than 3 days
    remove_archive_after_days(db_cursor, 3, False)

    # Verify that only the data from the last 3 days is present
    db_cursor.execute("SELECT * FROM metric_values")
    results = db_cursor.fetchall()
    assert len(results) == 1


def test_save_data_report(db_cursor):
    date = "2023-01-01"
    metric_id = insert_metric(db_cursor, "TEST_METRIC")

    metric_values = [
        {"usage": 20, "timestamp": "2023-01-01 10:30:00.000"},
        {"usage": 50, "timestamp": "2023-01-01 12:00:00.000"},
        {"usage": 80, "timestamp": "2023-01-01 15:45:00.000"},
        # Adding a value from another day
        {"usage": 30, "timestamp": "2023-01-02 11:00:00.000"},
    ]
    for value in metric_values:
        query_insert_metric_value = """
            INSERT INTO metric_values (metric_id, value, timestamp) VALUES (?, ?, ?)
            """
        db_cursor.execute(
            query_insert_metric_value,
            (metric_id, json.dumps(value["usage"]), value["timestamp"]),
        )
    db_cursor.connection.commit()

    data, date, _, _ = db_get_metric_values_from_day(db_cursor, date)
    metric_names = db_get_all_metrics(db_cursor)

    thresholds = {"GPU": 70, "CPU": 70, "RAM": 70}
    point_per_minute = 10
    date = "2023-01-01"

    save_data_report(
        db_cursor,
        date,
        data,
        metric_names,
        thresholds,
        point_per_minute,
    )

    db_cursor.execute("SELECT * FROM daily_reports")
    results = db_cursor.fetchall()
    assert len(results) == 1

    report = results[0]

    assert report[0] == date
    assert report[1] == True  # report_finished
    assert report[2] == "2023-01-01 10:30:00.000"  # first_timestamp
    assert report[3] == "2023-01-01 15:45:00.000"  # last_timestamp

    saved_daily_counts = json.loads(report[4])
    saved_daily_max = json.loads(report[5])
    saved_daily_avg = json.loads(report[6])

    assert saved_daily_counts == {"TEST_METRIC": 3}
    assert saved_daily_max == {"TEST_METRIC": 80.0}
    assert saved_daily_avg == {"TEST_METRIC": 50.0}
