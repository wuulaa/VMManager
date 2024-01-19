from src.domain_xml.xml_init import create_initial_xml
from src.utils.config import CONF
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
from src.volume.api import API
from src.guest.db import db as guestDB
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.utils.response import APIResponse
from src.network.api import NetworkAPI
from src.domain_xml.device import graphics
from src.domain_xml.device.disk import create_cdrom_builder
from src.volume.api import VolumeAPI
from src.utils.generator import UUIDGenerator
import src.utils.consts as consts 
import requests

status = {
    0:"nostate",
    1:"running",
    2:"blocked",
    3:"paused",
    4:"shutdown",
    5:"shutoff",
    6:"crashed",
    7:"pmsuspended"
}

vol_api = VolumeAPI()
networkapi = NetworkAPI()

class GuestService():
    @enginefacade.transactional
    def create_domain(self, session, domain_name: str, slave_name: str, **kwargs):
        exist_uuids = guestDB.get_domain_list()
        guest = create_initial_xml(domain_name)
        vol_api.clone_volume()

        vol_api.create_volume("a2d6b10a-8957-4648-8052-8371fb10f4e1", domain_name, 20*1024)
        rbdXML = RbdVolumeXMLBuilder()
        device = rbdXML.construct(domain_name)
        guest.devices.disk.append(device)
        guest.devices.disk.append(create_cdrom_builder(source_path="/home/kvm/images/ubuntu-22.04.3-live-server-arm64.iso", target_dev="sda"))
        url = CONF['slaves'][slave_name]
        xml = {consts.P_DOMAIN_XML : guest.get_xml_string(), consts.P_DOMAIN_NAME : domain_name}
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/addDomain/", data=xml).json())
        if(response.code == 0):
            uuid = response.get_data()['uuid']
            guestDB.create_guest(session, uuid, domain_name, slave_name, **kwargs)
        return response

    @enginefacade.transactional
    def shutdown_domain(self, session, domain_name: str, slave_name: str):
        uuid = guestDB.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/shutdownDomain/", data=data).json)
        if(response.code == 0):
            guestDB.status_update(session, uuid, status=status[5])
        return response

    @enginefacade.transactional
    def destroy_domain(self, session, domain_name: str, slave_name: str):
        uuid = guestDB.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/destroyDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, uuid, status=status[5])
        return response

    @enginefacade.transactional
    def pause_domain(self, session, domain_name: str, slave_name: str):
        uuid = guestDB.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/pauseDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, uuid, status=status[3])
        return response

    @enginefacade.transactional
    def resume_domain(self, session, domain_name: str, slave_name: str):
        uuid = guestDB.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/resumeDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, uuid, status=status[1])
        return response
    
    @enginefacade.transactional
    def reboot_domain(self, session, domain_name: str, slave_name: str):
        uuid = guestDB.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/rebootDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, uuid, status=status[1])
        return response

    @enginefacade.transactional
    def start_domain(self, session, domain_name: str, slave_name: str):
        uuid = guestDB.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/startDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, uuid, status=status[1])
        
        # this invoke is used for juding whether domain interfaces' ip is modified
        # while domain is not running. Related operations would be done within this func
        networkapi.domain_ip_modified(uuid)    
        
        return response

    @enginefacade.transactional
    def batch_start_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchStartDomains/", data=data).json())
        return response

    @enginefacade.transactional
    def batch_pause_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchPauseDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            guestDB.status_update(session, uuid, status[3])
        return response

    @enginefacade.transactional
    def batch_shutdown_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchShutdownDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            guestDB.status_update(session, uuid, status[4])
        return response

    @enginefacade.transactional
    def batch_delete_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchDeleteDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            guestDB.delete_domain_by_uuid(session, uuid)
        return response

    @enginefacade.transactional
    def batch_restart_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchRestartDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            guestDB.status_update(session, uuid, status[1])
        return response

    @enginefacade.transactional
    def get_domains_list(session):
        return guestDB.get_domain_list(session)

    @enginefacade.transactional
    def rename_domain(self, session, domain_name, new_name, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_NEW_NAME : new_name}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/renameDomain/", data=data).json())
        if(response.code == 0):
            uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
            guestDB.update_guest(session, uuid, values={"name": new_name})
        return response

    @enginefacade.transactional
    def put_description(self, session, domain_name, new_description, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_NEW_DESCRIPTION : new_description}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/putDes/", data=data).json())
        if(response.code == 0):
            uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
            guestDB.update_guest(session, uuid, values={"description": new_description})
        return response

    @enginefacade.transactional
    def delete_domain(self, session, domain_name, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/delDomain/", data=data).json())
        if(response.code == 0):
            uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
            guestDB.delete_domain_by_uuid(session, uuid = uuid)
        return response
    
    @enginefacade.transactional
    def attach_nic(self, session, domain_name, slave_name, interface_name, flags):
        domain_uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        response = networkapi.attach_interface_to_domain(domain_uuid, interface_name)
        xml = networkapi.get_interface_xml(interface_name)
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML : xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        res = networkapi.set_ip_in_domain(interface_name, False)
        return res
    
    
    @enginefacade.transactional
    def detach_nic(self, session, domain_name, slave_name, interface_name, flags):
        networkapi.set_ip_in_domain(interface_name, True)
        xml = networkapi.get_interface_xml(interface_name)
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML : xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/detachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        domain_uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        response = networkapi.detach_interface_from_domain(domain_uuid, interface_name)
        return response
    
    @enginefacade.transactional
    def list_nic(self, session, domain_name: str, slave_name: str):
        domain_uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        return networkapi.list_domain_interfaces(domain_uuid)
    
    
    @enginefacade.transactional
    def set_domain_vcpu(self, session, domain_name, slave_name, cpu_num, flags):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_CPU_NUM : cpu_num, consts.P_FLAGS : flags}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setCPU/", data=data).json())
        if(response.code == 0):
            uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
            guestDB.update_guest(session, uuid, values={"cpu": cpu_num})
        return response
    
    @enginefacade.transactional
    def set_domain_memory(self, session, domain_name, slave_name, memory_size, flags):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_MEMORY_SIZE : memory_size, consts.P_FLAGS : flags}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setMemory", data=data).json())
        if(response.code == 0):
            uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
            guestDB.update_guest(session, uuid, values={"memory": memory_size})
        return response
    
    
    @enginefacade.transactional
    def add_vnc(self, session, domain_name, slave_name, port: int, passwd: str, flags):
        xml = graphics.create_vnc_viewer(port, passwd).get_xml_string()
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        address = f"{url}:{port}:{passwd}"
        guestDB.update_guest(session, uuid, values={"vnc_address":address })
        return response
    
    
    @enginefacade.transactional
    def add_spice(self, session, domain_name, slave_name, port: int, passwd: str, flags):
        xml = graphics.create_spice_viewer(port, passwd).get_xml_string()
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        address = f"{url}:{port}:{passwd}"
        guestDB.update_guest(session, uuid, values={"spice_address":address })
        return response
    
    
    @enginefacade.transactional
    def change_graphic_passwd(self, session, domain_name: str, slave_name: str, port:int, passwd: str, flags, vnc=True):
        if vnc:
            xml = graphics.create_vnc_viewer(port, passwd).get_xml_string()
        else:
            xml = graphics.create_spice_viewer(port, passwd).get_xml_string() 
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        address = f"{url}:{port}:{passwd}"
        if vnc:
            guestDB.update_guest(session, uuid, values={"vnc_address":address })
        else:
            guestDB.update_guest(session, uuid, values={"spice_address":address })
        return response
        
        
    def monitor(self, domain_name: str, slave_name: str):
        data = {
            consts.P_DOMAIN_NAME : domain_name,
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/monitor/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        return response
        
        
    def set_user_passwd(self, domain_name: str, slave_name: str, user_name: str, passwd: str):
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_USER_NAME: user_name,
            consts.P_PASSWD: passwd
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setUserPasswd/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        return response
    
    def get_domain_slave_name(session, domain_uuid: str):
        return APIResponse.success(guestDB.get_domain_slave_name(session, domain_uuid))
    
    def get_domain_status(session, domain_uuid: str):
        return APIResponse.success(guestDB.get_domain_status(session, domain_uuid))
    
    @enginefacade.transactional
    def attach_domain_disk(self, session, domain_name, slave_name, volume_name, volume_uuid, size, flags):
        guest_uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
        if volume_uuid:
            response = vol_api.add_volume_to_guest(volume_uuid ,guest_uuid, return_xml =True)
            if response.is_success():
                xml = response.get_data()
            else:
                return response
        else:
            response: APIResponse = vol_api.create_volume(pool_uuid="d38681d3-07fd-41c7-b457-1667ef9354c7", volume_name=volume_name, allocation=size, guest_uuid=guest_uuid, return_xml = True)
            if response.is_success():
                xml = response.get_data()
            else:
                return response
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML : xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        return response
    

    @enginefacade.transactional
    def detach_domain_disk(self, session, domain_name, slave_name, volume_uuid, flags):
        response = vol_api.get_volume_by_uuid(volume_uuid, return_xml = True)
        if response.is_success():
            xml = response.get_data()
        else:
            return response
        data = {
            consts.P_DOMAIN_NAME : domain_name,
            consts.P_DEVICE_XML : xml,
            consts.P_FLAGS : flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/detachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
        return vol_api.remove_volume_from_guest(volume_uuid)

class SlaveService():
    @enginefacade.transactional
    def create_slave(self, session, slave_name: str, slave_address):
       slave = guestDB.create_slave(session, slave_name, slave_address)
       if slave:
           return APIResponse.success(data=slave.uuid)
      
    @enginefacade.transactional
    def delete_slave(self, session, slave_name: str):
        slave = guestDB.get_slave_by_name(session, slave_name)
        if slave is None:
            return APIResponse.error(code=400, msg=f"Cannot find a slave where name = {slave_name}")
        guestDB.delete_slave(session, slave_name)
        return APIResponse.success()
    
    @enginefacade.transactional
    def slave_detail(self, session, slave_name: str):
        slave = guestDB.get_slave_by_name(session, slave_name)
        if slave is None:
            return APIResponse.error(code=400, msg=f"Cannot find a slave where name = {slave_name}")
        data = slave.to_dict()
        return APIResponse.success(data)
    
    @enginefacade.transactional
    def get_slave_by_uuid(self, session, uuid: str):
       slave = guestDB.get_slave_by_uuid(session, uuid)
       return APIResponse.success(data=slave)
   
    @enginefacade.transactional
    def get_slave_by_name(self, session, name: str):
       slave = guestDB.get_slave_by_name(session, name)
       return APIResponse.success(data=slave)
       
    @enginefacade.transactional
    def get_slave_address(self, session, slave_name: str = None, uuid: str = None):
        if uuid:
            addr = guestDB.get_slave_address_by_uuid(session, uuid)
            return APIResponse.success(data=addr)
        else:
            uuid = guestDB.get_slave_uuid_by_name(session, slave_name)
            addr = guestDB.get_slave_address_by_uuid(session, uuid)
            return APIResponse.success(data=addr)
      
    @enginefacade.transactional
    def get_slave_guests(self, session, name: str):
       guests = guestDB.get_slave_guests(session, name)
       data = [guest.uuid for guest in guests]
       return APIResponse.success(data=data)
   
    @enginefacade.transactional
    def init_slave_db(self, session):
        slaves = CONF['slaves']
        res = []
        for key, value in slaves.items():
            slave_name = key
            slave_addr = value
            create_res =self.create_slave(session, slave_name, slave_addr).get_data()
            res.append(create_res)
        return APIResponse.success(data=res)
        
    @enginefacade.transactional
    def attach_domain_disk(self, session, domain_name, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDisk/", data=data).json())
        if(response.code == 0):
            uuid = guestDB.get_domain_uuid_by_name(session, domain_name, slave_name)
            guestDB.update_guest(session, uuid, values={})
        return response