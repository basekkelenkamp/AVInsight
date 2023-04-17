from flask import Flask, render_template
from flask_socketio import SocketIO
import psutil
import time
import threading

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
socket_io = SocketIO(app)


def get_cpu_usage():
    """Function to get CPU usage"""
    while True:
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)

        # Emit CPU usage to the connected clients
        socket_io.emit(
            "cpu_usage",
            {
                "data": [cpu_percent],
                "labels": [],
            },
            namespace="/test",
        )
        time.sleep(1)


@app.route("/")
def index():
    return render_template("index.html")


@socket_io.on("connect", namespace="/test")
def connect():
    """Event handler for socket.io connection"""
    print("Client connected")
    # Start a separate thread to get CPU usage in real-time
    thread = threading.Thread(target=get_cpu_usage)
    thread.daemon = True
    thread.start()


@socket_io.on("disconnect", namespace="/test")
def disconnect():
    """Event handler for socket.io disconnection"""
    print("Client disconnected")


if __name__ == "__main__":
    socket_io.run(app, debug=True)
