import json
import os
import sys
import shutil
from datetime import datetime


from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import time
import threading
from threading import Event

# from hwinfo.pci import PCIDevice
# from hwinfo.pci.lspci import LspciNNMMParser
from config.load_config import Config, get_config, update_config
from database.db import (
    db_get_all_metrics,
    db_init_connection,
    db_get_connection,
    db_get_metric_values_from_day,
    insert_metric_value,
    remove_archive_after_days,
)
from util.metrics import (
    get_cpu_usage,
    get_disk_io_counters,
    calculate_disk_read_speeds,
    get_disk_list,
    get_gpu_usage,
    get_ram_usage,
    get_metric_id_by_type,
)


#   ######   #
#    INIT    #
#   ######   #

# Init Nuikta for executable
if sys.argv[1] != "run":
    debug = False
    temp_dir = os.path.dirname(__file__)
    original_location = sys.argv[1]
    db_path = os.path.join(original_location, "database")
    for dir_name in ["templates", "static"]:
        src_dir = os.path.join(original_location, dir_name)
        dst_dir = os.path.join(temp_dir, dir_name)

        shutil.copytree(src_dir, dst_dir)

    # Init flask
    app = Flask(
        __name__,
        template_folder=os.path.join(temp_dir, "templates"),
        static_folder=os.path.join(temp_dir, "static"),
    )

# Init flask from poetry env
else:
    debug = True
    db_path = "database"
    app = Flask(__name__)


@app.template_filter("fromjson")
def from_json_filter(data):
    return json.loads(data)


app.config["SECRET_KEY"] = "secretkey"
app.jinja_env.filters["fromjson"] = from_json_filter
socket_io = SocketIO(app)

# Load the config
config: Config = get_config()

# Init db connection & remove archive
connection = db_init_connection(db_path=db_path)
metrics = db_get_all_metrics(connection.cursor(), as_obj=True)

archive_days = int(config.get_setting_value("clear_archive_after_days"))
print(f"removing archive older than {archive_days} days")
remove_archive_after_days(connection.cursor(), archive_days)
connection.close()


# Event to control the running threads
stop_event = Event()
threads = []


#   ######   #
#   SOCKET   #
#   ######   #


def get_metrics(original_config: Config):
    # Extract settings
    interval = float(original_config.get_setting_value("interval"))
    disk = original_config.get_setting_value("disk")
    archive_days = int(original_config.get_setting_value("clear_archive_after_days"))
    archive_GPU = original_config.get_setting_value("archive_GPU")
    archive_CPU = original_config.get_setting_value("archive_CPU")
    archive_RAM = original_config.get_setting_value("archive_RAM")
    archive_DISK = original_config.get_setting_value("archive_DISK")

    # archives to write to
    archives = [
        x[0]
        for x in [
            ("GPU", archive_GPU),
            ("CPU", archive_CPU),
            ("RAM", archive_RAM),
            ("DISK", archive_DISK),
        ]
        if x[1]
    ]

    # Timers
    prev_time = time.time()
    prev_disk_io = get_disk_io_counters(disk)

    while not stop_event.is_set():
        if json.dumps(original_config.to_dict()) != json.dumps(config.to_dict()):
            break

        # to keep track of function runtime speed
        start_time = time.time()

        print(
            f"archive: {archives} | disk: {disk} | interval: {interval} | del after days:{archive_days}"
        )

        # Get CPU, GPU, RAM
        cpu_percent = get_cpu_usage(interval)
        ram_percent = get_ram_usage()
        gpu_percent = get_gpu_usage()

        # Get disk read speed
        curr_time = time.time()
        curr_disk_io = get_disk_io_counters(disk)
        time_diff = curr_time - prev_time
        disk_read_speed = calculate_disk_read_speeds(
            prev_disk_io, curr_disk_io, time_diff
        )

        prev_time = curr_time
        prev_disk_io = curr_disk_io

        socket_io.emit("cpu-usage-chart", {"data": [cpu_percent]}, namespace="/metrics")
        socket_io.emit("gpu-usage-chart", {"data": [gpu_percent]}, namespace="/metrics")
        socket_io.emit("ram-usage-chart", {"data": [ram_percent]}, namespace="/metrics")
        socket_io.emit(
            "disk-read-speed-chart", {"data": [disk_read_speed]}, namespace="/metrics"
        )

        # Connect to the database, write data, then close the connection
        if archives:
            connection = db_get_connection(db_path=db_path)
            cursor = connection.cursor()
            for archive in archives:
                if archive == "GPU":
                    insert_metric_value(
                        cursor, get_metric_id_by_type(metrics, "GPU"), gpu_percent
                    )
                elif archive == "CPU":
                    insert_metric_value(
                        cursor, get_metric_id_by_type(metrics, "CPU"), cpu_percent
                    )
                elif archive == "RAM":
                    insert_metric_value(
                        cursor, get_metric_id_by_type(metrics, "RAM"), ram_percent
                    )
                elif archive == "DISK":
                    insert_metric_value(
                        cursor, get_metric_id_by_type(metrics, "DISK"), disk_read_speed
                    )

            connection.commit()
            connection.close()

        # Calculate function runtime & sleep amount
        elapsed_time = time.time() - start_time
        sleep_time = interval - elapsed_time

        if sleep_time > 0:
            time.sleep(sleep_time)


#   ######   #
#   ROUTES   #
#   ######   #


@app.route("/")
def index():
    return render_template(
        "index.html",
        interval=config.get_setting_value("interval"),
        threshold_GPU=config.get_setting_value("threshold_GPU"),
        threshold_CPU=config.get_setting_value("threshold_CPU"),
        threshold_RAM=config.get_setting_value("threshold_RAM"),
    )


@app.route("/config")
def config():
    # ['PhysicalDrive0', 'PhysicalDrive1', 'PhysicalDrive2']
    disks = get_disk_list()
    config = get_config()
    return render_template("config.html", config=config.to_dict(), disks=disks)


@app.route("/save-config", methods=["POST"])
def save_config():
    global config
    global keep_running
    new_config = request.json
    try:
        stop_metrics_thread()

        update_config(new_config)
        config = get_config()

        # Remove archive
        archive_days = int(config.get_setting_value("clear_archive_after_days"))
        connection = db_get_connection(db_path=db_path)
        cursor = connection.cursor()
        print(f"removing archive older than {archive_days} days")
        remove_archive_after_days(cursor, archive_days)
        connection.close()

        start_metrics_thread()

        return jsonify({"result": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"result": "error"}), 500


@app.route("/archive", defaults={"date": None})
@app.route("/archive/<date>")
def archive(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except:
        date = None

    connection = db_get_connection(db_path=db_path)
    cursor = connection.cursor()

    # Example date str: 'YYYY-MM-DD'
    data, date, prev_date, next_date = db_get_metric_values_from_day(cursor, date)
    metric_names = db_get_all_metrics(cursor)
    connection.close()

    return render_template(
        "archive.html",
        data=json.dumps(data),
        metric_names=json.dumps(metric_names),
        date=date,
        prev_date=prev_date,
        next_date=next_date,
    )


@socket_io.on("connect", namespace="/metrics")
def connect():
    """Event handler for socket.io connection"""
    print("Client connected")
    # Start a separate thread to get usage in real-time
    # start_metrics_thread()


@socket_io.on("disconnect", namespace="/metrics")
def disconnect():
    """Event handler for socket.io disconnection"""
    print("Client disconnected")


#   ######   #
#   THREAD   #
#   ######   #
def start_metrics_thread():
    global config
    global threads
    config = get_config()

    # Stop all previous threads
    for thread in threads:
        if thread.is_alive():
            stop_event.set()

    # Clear the threads list and the stop event
    threads = []
    stop_event.clear()

    # Start a new thread
    thread = threading.Thread(target=get_metrics, args=(config,))
    thread.daemon = True
    thread.start()

    # Add the new thread to the threads list
    threads.append(thread)


def stop_metrics_thread():
    # Stop the current thread
    stop_event.set()


#   ######   #
#   SERVER   #
#   ######   #

start_metrics_thread()
if __name__ == "__main__":
    port = int(
        os.environ.get("FLASK_PORT", 5000)
    )  # Use 5000 as the default port number
    url = f"http://localhost:{port}"

    socket_io.run(app, host="0.0.0.0", port=port, debug=debug)
