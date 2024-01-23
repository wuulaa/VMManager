import ipaddress

def get_network_gateway(ip_address_str: str) -> str:
    try:
        ip_interface = ipaddress.IPv4Interface(ip_address_str)
        network = ip_interface.network

        # 获取网络的第一个地址作为网关
        gateway_ip = str(network.network_address + 1)
        return f"{gateway_ip}/{network.prefixlen}"

    except ValueError as e:
        print(f"Error: {e}")
        return None

# 示例用法
ip_address_input = "20.0.0.11/24"
gateway = get_network_gateway(ip_address_input)

if gateway:
    print(f"The gateway for {ip_address_input} is {gateway}")
else:
    print("Failed to determine the gateway.")
