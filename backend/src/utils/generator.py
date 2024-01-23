import uuid
import ipaddress
import random
from faker import Faker
from typing import Optional


class UUIDGenerator(object):
    @staticmethod
    def get_uuid(exist_uuid: Optional[list] = []) -> str:
        ''' generate a non-conflicting UUID
        为了保证 UUID 的唯一性，新生成的 UUID 不能与已存在的
        重复，因此需要将过往的 UUID 作为参数传入进行对比。

        exist_uuid: 过往生成的 UUID
        @return 新生成的 UUID
        '''
        for ignore in range(256):
            gen_uuid = str(uuid.uuid4())
            if (gen_uuid in exist_uuid):
                continue
            return gen_uuid
        raise Exception("Failed to generate non-conflicting UUID")


def generate_unique_ip(network_str: str, used_ips: list[str]) -> str:
    """
    Get an unused IP address from the network.
    """
    network = ipaddress.IPv4Network(network_str, strict=False)
    available_ips = [str(ip) for ip in network.hosts()]
    unused_ips = set(available_ips) - set(used_ips)

    # If there are unused IP addresses, return the first one
    if unused_ips:
        unused_ip = unused_ips.pop()
        return f"{unused_ip}/{network.prefixlen}"
    else:
        return None
   
    
def generage_unused_name(old_name_list: list[str]):
    """
    get a name , and it's not in the list
    """
    faker = Faker()
    while True:
        name: str = faker.name()
        if old_name_list.count(name) < 1:
            return name.replace(" ","")
        

def get_network_gateway(ip_address_str: str) -> str:
    try:
        ip_interface = ipaddress.IPv4Interface(ip_address_str)
        network = ip_interface.network

        # 获取网络的第一个地址作为网关
        gateway_ip = str(network.network_address + 1)
        return gateway_ip

    except ValueError as e:
        print(f"Error: {e}")
        return None

def generate_random_mac():
    """Generate a random MAC address.

    00-16-3E allocated to xensource
    52-54-00 used by qemu/kvm
    Different hardware firms have their own unique OUI for mac address.
    The OUI list is available at https://standards.ieee.org/regauth/oui/oui.txt.

    The remaining 3 fields are random, with the first bit of the first
    random field set 0.
    """
    oui = [0x52, 0x54, 0x00]
    mac = oui + [
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)]
    return ':'.join(["%02x" % x for x in mac])