import psutil
import time
from src.utils.response import APIResponse

def convert_bytes_to_gb(bytes_value):
    return bytes_value / (1024 ** 3)

def get_cpu_info():
    cpu_count = psutil.cpu_count()
    cpu_usage = psutil.cpu_percent(interval=1)
    return {'cpu_count': cpu_count, 'cpu_usage': cpu_usage}

def get_memory_info():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    total_memory = convert_bytes_to_gb(memory.total)
    available_memory = convert_bytes_to_gb(memory.available)
    used_memory = convert_bytes_to_gb(memory.used)
    memory_usage = memory.percent
    total_swap = convert_bytes_to_gb(swap.total)
    used_swap = convert_bytes_to_gb(swap.used)
    swap_usage = swap.percent
    return {
        'total_memory': total_memory,
        'available_memory': available_memory,
        'used_memory': used_memory,
        'memory_usage': memory_usage,
        'total_swap': total_swap,
        'used_swap': used_swap,
        'swap_usage': swap_usage
    }

def get_network_info():
    network = psutil.net_io_counters()
    bytes_sent = convert_bytes_to_gb(network.bytes_sent)
    bytes_recv = convert_bytes_to_gb(network.bytes_recv)
    return {'bytes_sent': bytes_sent, 'bytes_recv': bytes_recv}

def get_all_node_info():
    # Get CPU information
    cpu_info = get_cpu_info()
    # Get memory information
    memory_info = get_memory_info()
    # Get network information
    network_info = get_network_info()
    info = {
        "time": time.localtime(), 
        "cpu": cpu_info,
        "memory": memory_info,
        "network": network_info
    }
    
    return APIResponse.success(info)


