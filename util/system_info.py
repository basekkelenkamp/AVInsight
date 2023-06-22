import platform
import psutil
from gpustat.core import GPUStatCollection


def _get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_pc_info():
    cpu_info = []

    uname = platform.uname()
    cpu_info.append(f"{uname.processor}")
    cpu_info.append(f"Total cores: {psutil.cpu_count(logical=True)}")
    cpu_info.append(f"Current Frequency: {psutil.cpu_freq().current:.2f}Mhz")
    
    svmem = psutil.virtual_memory()
    print(f"Total: {_get_size(svmem.total)}")
    print(f"Available: {_get_size(svmem.available)}")
    
    ram_info = []
    ram_info.append(f"Total ram: {_get_size(svmem.total)}")

    gpu_info = []
    gpustats = GPUStatCollection.new_query()
    for gpu in gpustats:
        gpu_info.append(f"{gpu.name}")
        gpu_info.append(f"Temperature: {gpu.temperature}°C")

    return {
        "CPU": cpu_info, 
        "GPU": gpu_info, 
        "RAM": ram_info, 
        }
