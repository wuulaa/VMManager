from src.domain_xml.xml_init import create_initial_xml
from src.utils.config import CONF
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
from src.volume.api import API
from src.guest.service import GuestService
import requests

guestService = GuestService()
vol_api = API()

def create_domain(domain_name: str, slave_name: str):
    guest = create_initial_xml(domain_name)
    vol_api.create_volume("a2d6b10a-8957-4648-8052-8371fb10f4e1", domain_name, 20*1024)
    rbdXML = RbdVolumeXMLBuilder()
    device = rbdXML.construct(domain_name)
    guest.devices.disk.append(device)
    url = CONF['slaves'][slave_name]
    data = {"domain_xml":guest.get_xml_string()}
    response: requests.Response = requests.post(url="http://"+url+"/addDomain/", data=data)
    return str(response.content)


def shutdown_domain(domain_name: str, slave_name: str):
    data = {"domain_name":domain_name}
    url = CONF['slaves'][slave_name]
    response: requests.Response = requests.post(url="http://"+url+"/shutdownDomain/", data=data)
    return str(response.content)


def destroy_domain(domain_name: str, slave_name: str):
    data = {"domain_name":domain_name}
    url = CONF['slaves'][slave_name]
    response: requests.Response = requests.post(url="http://"+url+"/destroyDomain/", data=data)
    return str(response.content)


def start_domain(domain_name: str, slave_name: str):
    data = {"domain_name":domain_name}
    url = CONF['slaves'][slave_name]
    response: requests.Response = requests.post(url="http://"+url+"/startDomain/", data=data)
    return str(response.content)


#to do
def clone_domain(domain_name: str, child_name: str, slave_name: str):
    vm_uuid = guestService.get_uuid_by_name(domain_name)
    volumes = vol_api.get_volumes_by_vm_uuid(vm_uuid)
    data = {"domainName":domain_name, "childName":child_name}
    url = CONF['slaves'][slave_name]
    response: requests.Response = requests.post(url="http://"+url+"/cloneDomain/", data=data)
    return str(response.content)



    