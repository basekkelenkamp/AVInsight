import json
import os
import sys
import shutil


from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import time
import threading

# from hwinfo.pci import PCIDevice
# from hwinfo.pci.lspci import LspciNNMMParser
from config.load_config import Config, get_config, update_config
from database.db import (
    db_get_all_metrics,
    db_init_connection,
    db_get_connection,
    db_get_today_metric_values,
    insert_metric_value,
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
config = get_config()

# Init db connection
connection = db_init_connection(db_path=db_path)
metrics = db_get_all_metrics(connection.cursor(), as_obj=True)
connection.close()

# Global flag to control the running thread
keep_running = True


#   ######   #
#   SOCKET   #
#   ######   #


def get_metrics(original_config: Config):
    interval = original_config.interval
    disk = original_config.disk
    enable_archive = original_config.enable_archive
    archive_days = original_config.clear_archive_after_days

    prev_time = time.time()
    prev_disk_io = get_disk_io_counters(disk)

    while keep_running:
        if json.dumps(original_config.get_params()) != json.dumps(config.get_params()):
            break

        # to keep track of function runtime speed
        start_time = time.time()

        print(
            f"archive: {enable_archive}| disk: {disk}| interval: {interval}| days:{archive_days}"
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
        if enable_archive:
            connection = db_get_connection(db_path=db_path)
            cursor = connection.cursor()
            insert_metric_value(
                cursor, get_metric_id_by_type(metrics, "CPU"), cpu_percent
            )
            insert_metric_value(
                cursor, get_metric_id_by_type(metrics, "GPU"), gpu_percent
            )
            insert_metric_value(
                cursor, get_metric_id_by_type(metrics, "RAM"), ram_percent
            )
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
    return render_template("index.html")


@app.route("/config")
def config():
    config_data = get_config(no_object=True)
    disks = get_disk_list()
    # ['PhysicalDrive0', 'PhysicalDrive1', 'PhysicalDrive2']
    return render_template("config.html", config=config_data, disks=disks)


@app.route("/save-config", methods=["POST"])
def save_config():
    global config
    global keep_running
    new_config = request.json
    try:
        stop_metrics_thread()

        update_config(new_config)
        config = get_config()

        start_metrics_thread()

        return jsonify({"result": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"result": "error"}), 500


@app.route("/archive")
def archive():
    connection = db_get_connection(db_path=db_path)
    cursor = connection.cursor()

    data = db_get_today_metric_values(cursor)
    metric_names = db_get_all_metrics(cursor)
    connection.close()

    return render_template(
        "archive.html", data=json.dumps(data), metric_names=json.dumps(metric_names)
    )


@socket_io.on("connect", namespace="/metrics")
def connect():
    global config
    global keep_running

    """Event handler for socket.io connection"""
    print("Client connected")
    # Start a separate thread to get usage in real-time
    start_metrics_thread()


@socket_io.on("disconnect", namespace="/metrics")
def disconnect():
    """Event handler for socket.io disconnection"""
    print("Client disconnected")


# Threading
def start_metrics_thread():
    global config
    global keep_running
    # Start a separate thread to get usage in real-time
    config = get_config()
    keep_running = True
    thread = threading.Thread(target=get_metrics, args=(config,))
    thread.daemon = True
    thread.start()


def stop_metrics_thread():
    global keep_running
    global config
    # Stop the current thread
    keep_running = False
    time.sleep(1)


#   ######   #
#   SERVER   #
#   ######   #

if __name__ == "__main__":
    port = int(
        os.environ.get("FLASK_PORT", 5000)
    )  # Use 5000 as the default port number
    url = f"http://localhost:{port}"

    socket_io.run(app, host="0.0.0.0", port=port, debug=debug)
