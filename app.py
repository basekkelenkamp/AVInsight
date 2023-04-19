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


def get_metrics():
    disk_name = "disk0"  # Replace with the disk name you want to monitor
    prev_time = time.time()
    prev_disk_io = psutil.disk_io_counters(perdisk=True)[disk_name].read_bytes

    while True:
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        # gpu_percent = get_gpu_usage('mac')

        virtual_memory = psutil.virtual_memory()
        ram_percent = virtual_memory.percent
        total_memory = virtual_memory.total
        used_memory = virtual_memory.used

        # Calculate disk read speed
        curr_time = time.time()
        curr_disk_io = psutil.disk_io_counters(perdisk=True)[disk_name].read_bytes
        time_diff = curr_time - prev_time
        read_bytes_diff = curr_disk_io - prev_disk_io
        disk_read_speed = read_bytes_diff / time_diff

        prev_time = curr_time
        prev_disk_io = curr_disk_io

        # available_memory = virtual_memory.available
        # free_memory = virtual_memory.free

        # Emit CPU usage to the connected clients
        socket_io.emit(
            "cpu-usage-chart",
            {
                "data": [cpu_percent],
                "labels": [],
            },
            namespace="/metrics",
        )
        socket_io.emit(
            "ram-usage-chart",
            {
                "data": [ram_percent],
                "labels": [],
            },
            namespace="/metrics",
        )

        socket_io.emit(
            "disk-read-speed-chart",
            {
                "data": [disk_read_speed],
                "labels": [],
            },
            namespace="/metrics",
        )

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
    socket_io.run(app, debug=True)
