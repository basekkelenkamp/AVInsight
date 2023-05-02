import os

import gpustat
from flask import Flask, render_template
from flask_socketio import SocketIO
import psutil
import time
import threading
import subprocess
from hwinfo.pci import PCIDevice
from hwinfo.pci.lspci import LspciNNMMParser


app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
socket_io = SocketIO(app)


def get_disk_io_counters():
    return {disk_name: disk.read_bytes for disk_name, disk in psutil.disk_io_counters(perdisk=True).items()}

def calculate_disk_read_speeds(prev_disk_io, curr_disk_io, time_diff):
    return {
        disk_name: (curr_disk_io[disk_name] - prev_disk_io[disk_name]) / time_diff
        for disk_name in curr_disk_io.keys()
    }

def get_metrics():
    prev_time = time.time()
    prev_disk_io = get_disk_io_counters()

    while True:
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        ram_percent = psutil.virtual_memory().percent
        
        curr_time = time.time()
        curr_disk_io = get_disk_io_counters()
        time_diff = curr_time - prev_time
        disk_read_speeds = calculate_disk_read_speeds(prev_disk_io, curr_disk_io, time_diff)

        prev_time = curr_time
        prev_disk_io = curr_disk_io

        socket_io.emit("cpu-usage-chart", {"data": [cpu_percent]}, namespace="/metrics")
        socket_io.emit("ram-usage-chart", {"data": [ram_percent]}, namespace="/metrics")
        socket_io.emit("disk-read-speed-chart", {"data": disk_read_speeds}, namespace="/metrics")

        time.sleep(0.1)



def get_gpu_usage(gpu_type="nvidia"):
    if gpu_type == "nvidia":
        try:
            gpu_stats = gpustat.new_query()
            return gpu_stats.gpus[0].utilization
        except Exception as e:
            print(f"Failed to get GPU usage: {e}")
            return 0.0
    else:
        try:
            output = subprocess.check_output(["intel_gpu_top", "-J"])
            return float(
                output.decode("utf-8").strip().split("\n")[1].split(":")[1].strip()
            )

        except subprocess.CalledProcessError:
            # Handle any errors that may occur during command execution
            print("Error: Failed to get GPU usage.")
            return None


@app.route("/")
def index():
    return render_template("index.html")


@socket_io.on("connect", namespace="/metrics")
def connect():
    """Event handler for socket.io connection"""
    print("Client connected")
    # Start a separate thread to get CPU usage in real-time
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
