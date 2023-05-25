import gpustat
import psutil
import subprocess


def get_disk_list():
    return [
        disk_name for disk_name, disk in psutil.disk_io_counters(perdisk=True).items()
    ]


def get_disk_io_counters(disk):
    data = {
        disk_name: disk.read_bytes
        for disk_name, disk in psutil.disk_io_counters(perdisk=True).items()
    }

    return data[disk]


def calculate_disk_read_speeds(prev_disk_io, curr_disk_io, time_diff):
    return (curr_disk_io - prev_disk_io) / time_diff


def get_cpu_usage(interval):
    return psutil.cpu_percent(interval=interval, percpu=False)


def get_ram_usage():
    return psutil.virtual_memory().percent


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


def get_metric_id_by_type(metrics, metric_type):
    for metric in metrics:
        if metric.type == metric_type:
            return metric.id
    return None  # return None if no matching metric is found
