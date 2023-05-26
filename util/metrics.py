from collections import defaultdict
from datetime import datetime
from math import ceil
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


def calculate_data_report(metric_names, data, point_per_minute, thresholds):
    new_data = defaultdict(lambda: defaultdict(list))
    id_to_type = {metric["id"]: metric["type"] for metric in metric_names}
    id_to_threshold = {
        metric["id"]: threshold for metric, threshold in zip(metric_names, thresholds)
    }

    # Initialize daily data structures
    daily_totals = defaultdict(int)
    daily_counts = defaultdict(int)
    daily_min = defaultdict(lambda: float("inf"))
    daily_max = defaultdict(float)

    for d in data:
        metric_id = d["metric_id"]
        metric_type = id_to_type[metric_id]
        threshold = id_to_threshold[metric_id]
        minute = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S.%f").strftime(
            "%H:%M"
        )
        value = float(d["value"])
        timestamp = d["timestamp"]
        new_data[metric_type][minute].append((timestamp, value))

        # Update daily totals and counts
        daily_totals[metric_type] += value
        daily_counts[metric_type] += 1
        daily_min[metric_type] = min(daily_min[metric_type], value)
        daily_max[metric_type] = max(daily_max[metric_type], value)

    # Calculate daily averages
    daily_avg = {
        metric_type: daily_totals[metric_type] / daily_counts[metric_type]
        for metric_type in daily_totals
    }

    # Post processing
    final_data = defaultdict(dict)
    for metric_type, minutes in new_data.items():
        metric_id = list(id_to_type.keys())[
            list(id_to_type.values()).index(metric_type)
        ]  # get the id from the type
        for minute, values in minutes.items():
            values.sort()  # sort by timestamp

            average = sum(v for _, v in values) / len(values)
            min_ = min(v for _, v in values)
            max_ = max(v for _, v in values)

            threshold_values = [
                (t, v) for t, v in values if v >= id_to_threshold[metric_id]
            ]
            if len(values) <= point_per_minute:
                final_values = values
            else:
                n = ceil(len(values) / point_per_minute)
                remaining_values = [values[i] for i in range(0, len(values), n)]

                # Keep the threshold values and the evenly spread remaining values
                final_values = threshold_values + remaining_values
                final_values.sort()  # sort by timestamp

            final_data[metric_type][minute] = {
                "avg": average,
                "minmax": [min_, max_],
                "values": final_values,
            }

        # Add daily averages, min, max to final_data
        final_data[metric_type]["daily"] = {
            "avg": daily_avg[metric_type],
            "min": daily_min[metric_type],
            "max": daily_max[metric_type],
        }

    # store
    return final_data, daily_counts, daily_max, daily_avg
