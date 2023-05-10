import os

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import time
import threading
from hwinfo.pci import PCIDevice
from hwinfo.pci.lspci import LspciNNMMParser
from config.load_config import get_config, update_config
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
    get_gpu_usage,
    get_ram_usage,
    get_metric_id_by_type,
)

# Init flask
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
socket_io = SocketIO(app)

# Load the config
config = get_config()

# Init db connection
connection = db_init_connection()
metrics = db_get_all_metrics(connection.cursor())
connection.close()


def get_metrics(interval=1):
    prev_time = time.time()
    prev_disk_io = get_disk_io_counters()

    while True:
        # Get CPU, GPU, RAM
        cpu_percent = get_cpu_usage(interval)
        ram_percent = get_ram_usage()
        gpu_percent = get_gpu_usage()

        # Get disk read speed
        curr_time = time.time()
        curr_disk_io = get_disk_io_counters()
        time_diff = curr_time - prev_time
        disk_read_speeds = calculate_disk_read_speeds(
            prev_disk_io, curr_disk_io, time_diff
        )

        prev_time = curr_time
        prev_disk_io = curr_disk_io

        socket_io.emit("cpu-usage-chart", {"data": [cpu_percent]}, namespace="/metrics")
        socket_io.emit("gpu-usage-chart", {"data": [gpu_percent]}, namespace="/metrics")
        socket_io.emit("ram-usage-chart", {"data": [ram_percent]}, namespace="/metrics")
        socket_io.emit(
            "disk-read-speed-chart", {"data": disk_read_speeds}, namespace="/metrics"
        )

        # Connect to the database, write data, then close the connection
        connection = db_get_connection()
        cursor = connection.cursor()
        insert_metric_value(cursor, get_metric_id_by_type(metrics, "CPU"), cpu_percent)
        insert_metric_value(cursor, get_metric_id_by_type(metrics, "GPU"), gpu_percent)
        insert_metric_value(cursor, get_metric_id_by_type(metrics, "RAM"), ram_percent)
        insert_metric_value(
            cursor, get_metric_id_by_type(metrics, "DISK"), disk_read_speeds
        )
        connection.commit()
        connection.close()

        time.sleep(interval)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/config")
def config():
    config_data = get_config()
    return render_template("config.html", config=config_data)


@app.route("/save-config", methods=["POST"])
def save_config():
    new_config = request.json
    # Your update_config function should be implemented here
    try:
        update_config(new_config)
        return jsonify({"result": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"result": "error"}), 500


@app.route("/archive")
def archive():
    return render_template("archive.html")


@socket_io.on("connect", namespace="/metrics")
def connect():
    """Event handler for socket.io connection"""
    print("Client connected")
    # Start a separate thread to get usage in real-time
    thread = threading.Thread(target=get_metrics)
    thread.daemon = True
    thread.start()


@socket_io.on("disconnect", namespace="/metrics")
def disconnect():
    """Event handler for socket.io disconnection"""
    print("Client disconnected")


if __name__ == "__main__":
    port = int(
        os.environ.get("FLASK_PORT", 5000)
    )  # Use 5000 as the default port number
    url = f"http://localhost:{port}"

    socket_io.run(app, host="0.0.0.0", port=port, debug=True)
