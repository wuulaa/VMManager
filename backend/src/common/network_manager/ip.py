import subprocess

def ip_link_set_up(interface_name: str):
    command = f"ip link set {interface_name} up"
    subprocess.run(command, shell=True)
    
def ip_addr_add(interface_name: str, address:str):
    command = f"ip addr add {address} dev {interface_name}"
    subprocess.run(command, shell=True)
    
def ip_addr_del(interface_name: str, address:str):
    command = f"ip addr del {address} dev {interface_name}"
    subprocess.run(command, shell=True)