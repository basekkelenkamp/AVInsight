import json
from math import ceil
import sqlite3
from datetime import datetime, timedelta
import pytz
from database.models import DataReport, Metric, MetricValue
import os
import zlib
from util.date_tools import is_date_today

from util.metrics import calculate_data_report

db_name = "AVInsight.db"


def db_get_connection(db_path: str):
    return sqlite3.connect(os.path.join(db_path, db_name), check_same_thread=False)


def db_init_connection(db_path: str):
    connection = sqlite3.connect(
        os.path.join(db_path, db_name), check_same_thread=False
    )
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

        # Commit the table creation & metrics
        connection.commit()

    # set to True to reset db
    clear_db = False
    if clear_db:
        cursor.execute("DROP TABLE IF EXISTS metrics")
        cursor.execute("DROP TABLE IF EXISTS metric_values")
        print("DROPPED TABLES")
        connection.commit()

    return connection


def insert_metric(cursor: sqlite3.Cursor, type: str):
    query_insert_metric = """
        INSERT INTO metrics (type) VALUES (?)
        """
    cursor.execute(query_insert_metric, (type,))
    return cursor.lastrowid


def insert_metric_value(cursor: sqlite3.Cursor, metric_id: int, value: str):
    berlin_tz = pytz.timezone("Europe/Berlin")
    current_time_berlin = datetime.now(berlin_tz)

    query_insert_metric = """
        INSERT INTO metric_values (metric_id, value, timestamp) VALUES (?, ?, ?)
        """

    cursor.execute(
        query_insert_metric,
        (
            metric_id,
            json.dumps(value),
            current_time_berlin.strftime("%Y-%m-%d %H:%M:%S.%f")[:-4],
        ),
    )
    return


def db_get_all_metrics(cursor: sqlite3.Cursor, as_obj: bool = False):
    query_get_metrics = """
        SELECT * FROM metrics 
        """

    metrics = []
    cursor.execute(query_get_metrics)
    results = cursor.fetchall()

    for result in results:
        if as_obj:
            metric = Metric(*result)
        else:
            metric = {
                "id": result[0],
                "type": result[1],
            }

        metrics.append(metric)

    return metrics


def db_get_metric_values_from_day(
    cursor: sqlite3.Cursor, custom_date: str = None, as_obj: bool = False
):
    berlin_tz = pytz.timezone("Europe/Berlin")

    if not custom_date:
        day = datetime.now(berlin_tz)
        next_date = None
    else:
        # Example incoming str: 'YYYY-MM-DD'
        day = datetime.strptime(custom_date, "%Y-%m-%d")
        day = berlin_tz.localize(day)
        next_date = day + timedelta(days=1)
        next_date = next_date.strftime("%Y-%m-%d")

    # Define the start and end of the day in Berlin time
    start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    if start_of_day.date() == datetime.now(berlin_tz).date():
        next_date = None

    query_get_metric_values = """
        SELECT * FROM metric_values 
        WHERE timestamp BETWEEN ? AND ?
        """

    cursor.execute(
        query_get_metric_values,
        (
            start_of_day.strftime("%Y-%m-%d %H:%M:%S.%f"),
            end_of_day.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),
    )
    results = cursor.fetchall()

    metric_values = []
    for result in results:
        if as_obj:
            metric_value = MetricValue(*result)
        else:
            metric_value = {
                "id": result[0],
                "metric_id": result[1],
                "timestamp": result[2],
                "value": result[3],
            }
        metric_values.append(metric_value)

    prev_date = day - timedelta(days=1)
    return (
        metric_values,
        day.strftime("%Y-%m-%d"),
        prev_date.strftime("%Y-%m-%d"),
        next_date,
    )


def remove_archive_after_days(cursor: sqlite3.Cursor, days: int, keep_reports: bool):
    berlin_tz = pytz.timezone("Europe/Berlin")
    current_time_berlin = datetime.now(berlin_tz)
    cutoff_time = current_time_berlin - timedelta(days=days)

    query_remove_old_records = """
        DELETE FROM metric_values
        WHERE timestamp < ?
        """

    cursor.execute(
        query_remove_old_records, (cutoff_time.strftime("%Y-%m-%d %H:%M:%S.%f"),)
    )
    cursor.connection.commit()

    if not keep_reports:
        query_remove_old_reports = """
            DELETE FROM daily_reports
            WHERE date_id < ?
            """

        cursor.execute(query_remove_old_reports, (cutoff_time.strftime("%Y-%m-%d"),))

    cursor.connection.commit()


def save_data_report(
    cursor: sqlite3.Cursor,
    date: str,
    data,
    metric_names,
    thresholds: dict = {"GPU": 70, "CPU": 70, "RAM": 70},
    point_per_minute: int = 10,
):
    berlin_tz = pytz.timezone("Europe/Berlin")

    date_ = datetime.strptime(date, "%Y-%m-%d")
    date_ = berlin_tz.localize(date_)

    report_finished = True
    if is_date_today(date):
        report_finished = False

    (
        final_data,
        daily_counts,
        daily_max,
        daily_avg,
    ) = calculate_data_report(metric_names, data, point_per_minute, thresholds)

    compressed_minute_data = zlib.compress(bytes(json.dumps(final_data), "utf-8"))

    query_insert_data_report = """
        INSERT INTO daily_reports (date_id, report_finished, first_timestamp, last_timestamp, daily_counts, daily_max, daily_avg, thresholds, total_points_count, minute_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    first_timestamp = data[0]["timestamp"]
    last_timestamp = data[-1]["timestamp"]

    print(f"Creating data report: {date}")
    cursor.execute(
        query_insert_data_report,
        (
            date,
            report_finished,  # Assuming the report is finished
            first_timestamp,
            last_timestamp,
            json.dumps(daily_counts),
            json.dumps(daily_max),
            json.dumps(daily_avg),
            json.dumps(thresholds),
            json.dumps(sum(daily_counts.values())),
            compressed_minute_data,
        ),
    )

    return date


def get_data_report(cursor: sqlite3.Cursor, date_id: str):
    query_get_data_report = """
        SELECT * FROM daily_reports WHERE date_id = ?
        """

    cursor.execute(query_get_data_report, (date_id,))
    result = cursor.fetchone()

    if result is None:
        return None

    data_report = DataReport(
        date_id=result[0],
        report_finished=bool(result[1]),
        first_timestamp=result[2],
        last_timestamp=result[3],
        daily_counts=result[4],
        daily_max=result[5],
        daily_avg=result[6],
        thresholds=result[7],
        total_points_count=result[8],
        minute_data=zlib.decompress(result[9]).decode("utf-8"),
    )

    return data_report


def remove_data_report(cursor: sqlite3.Cursor, date_id: str):
    query_remove_data_report = """
        DELETE FROM daily_reports WHERE date_id = ?
        """

    print(f"Removing data report: {date_id}")
    cursor.execute(query_remove_data_report, (date_id,))
