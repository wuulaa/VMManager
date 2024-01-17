from src.domain_xml.xml_init import create_initial_xml
from src.utils.config import CONF
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
from src.volume.api import API
from src.guest.db import db as db
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.utils.response import APIResponse
from src.network.api import NetworkAPI
from src.domain_xml.device import graphics
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

vol_api = API()
networkapi = NetworkAPI()

class GuestService():
    @enginefacade.transactional
    def create_domain(self, session, domain_name: str, slave_name: str, **kwargs):
        guest = create_initial_xml(domain_name)
        vol_api.create_volume("a2d6b10a-8957-4648-8052-8371fb10f4e1", domain_name, 20*1024)
        rbdXML = RbdVolumeXMLBuilder()
        device = rbdXML.construct(domain_name)
        guest.devices.disk.append(device)
        url = CONF['slaves'][slave_name]
        data = {consts.P_DOMAIN_XML : guest.get_xml_string(), consts.P_DOMAIN_NAME : domain_name}
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/addDomain/", data=data).json())
        if(response.code == 0):
            uuid = response.get_data()['uuid']
            db.create_guest(session, uuid, domain_name, slave_name, **kwargs)
        return response

    @enginefacade.transactional
    def shutdown_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/shutdownDomain/", data=data).json)
        if(response.code == 0):
            db.status_update(session, uuid, status=status[5])
        return response

    @enginefacade.transactional
    def destroy_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/destroyDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[5])
        return response

    @enginefacade.transactional
    def pause_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/pauseDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[3])
        return response

    @enginefacade.transactional
    def resume_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/resumeDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[1])
        return response

    @enginefacade.transactional
    def start_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_domain_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/startDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[1])
        
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
            db.status_update(session, uuid, status[3])
        return response

    @enginefacade.transactional
    def batch_shutdown_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchShutdownDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            db.status_update(session, uuid, status[4])
        return response

    @enginefacade.transactional
    def batch_delete_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchDeleteDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            db.delete_domain_by_uuid(session, uuid)
        return response

    @enginefacade.transactional
    def batch_restart_domains(self, session, domains_name_list, slave_name: str):
        data = {consts.P_DOMAINS_NAME_LIST : domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchRestartDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            db.status_update(session, uuid, status[1])
        return response

    @enginefacade.transactional
    def get_domains_list(session):
        return db.get_domain_list(session)

    @enginefacade.transactional
    def rename_domain(self, session, domain_name, new_name, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_NEW_NAME : new_name}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/renameDomain/", data=data).json())
        if(response.code == 0):
            uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
            db.update_guest(session, uuid, values={"name": new_name})
        return response

    @enginefacade.transactional
    def put_description(self, session, domain_name, new_description, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_NEW_DESCRIPTION : new_description}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/putDes/", data=data).json())
        if(response.code == 0):
            uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
            db.update_guest(session, uuid, values={"description": new_description})
        return response

    @enginefacade.transactional
    def delete_domain(self, session, domain_name, slave_name):
        data = {consts.P_DOMAIN_NAME : domain_name}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/delDomain/", data=data).json())
        if(response.code == 0):
            uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
            db.delete_domain_by_uuid(session, uuid = uuid)
        return response
    
    @enginefacade.transactional
    def attach_nic(self, session, domain_name, slave_name, interface_name, flags):
        domain_uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
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
        return response
    
    
    @enginefacade.transactional
    def detach_nic(self, session, domain_name, slave_name, interface_name, flags):
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
        domain_uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
        response = networkapi.detach_interface_from_domain(domain_uuid, interface_name)
        return response
    
    @enginefacade.transactional
    def list_nic(self, session, domain_name: str, slave_name: str):
        domain_uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
        return networkapi.list_domain_interfaces(domain_uuid)
    
    
    @enginefacade.transactional
    def set_domain_vcpu(self, session, domain_name, slave_name, cpu_num, flags):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_CPU_NUM : cpu_num, consts.P_FLAGS : flags}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setCPU/", data=data).json())
        if(response.code == 0):
            uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
            db.update_guest(session, uuid, values={"cpu": cpu_num})
        return response
    
    @enginefacade.transactional
    def set_domain_memory(self, session, domain_name, slave_name, memory_size, flags):
        data = {consts.P_DOMAIN_NAME : domain_name, consts.P_MEMORY_SIZE : memory_size, consts.P_FLAGS : flags}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setMemory", data=data).json())
        if(response.code == 0):
            uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
            db.update_guest(session, uuid, values={"memory": memory_size})
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
        uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
        address = f"{url}:{port}:{passwd}"
        db.update_guest(session, uuid, values={"vnc_address":address })
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
        uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
        address = f"{url}:{port}:{passwd}"
        db.update_guest(session, uuid, values={"spice_address":address })
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
        uuid = db.get_domain_uuid_by_name(session, domain_name, slave_name)
        address = f"{url}:{port}:{passwd}"
        if vnc:
            db.update_guest(session, uuid, values={"vnc_address":address })
        else:
            db.update_guest(session, uuid, values={"spice_address":address })
        return response
        
        
    def monitor(self, domain_name: str, slave_name: str):
        data = {
            consts.P_DOMAIN_NAME : domain_name,
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/monitor/", data=data).json())
        if response.code != 0:
            return APIResponse.error(msg=response.msg)
    
    def get_domain_slave_name(session, domain_uuid: str):
        return APIResponse.success(db.get_domain_slave_name(session, domain_uuid))
    
    def get_domain_status(session, domain_uuid: str):
        return APIResponse.success(db.get_domain_status(session, domain_uuid))
    

class SlaveService():
    @enginefacade.transactional
    def create_slave(self, session, slave_name: str, slave_address):
       slave = db.create_slave(session, slave_name, slave_address)
       if slave:
           return APIResponse.success(data=slave.uuid)
       
    @enginefacade.transactional
    def get_slave_by_uuid(self, session, uuid: str):
       slave = db.get_slave_by_uuid(session, uuid)
       return APIResponse.success(data=slave)
   
    @enginefacade.transactional
    def get_slave_by_name(self, session, name: str):
       slave = db.get_slave_by_name(session, name)
       return APIResponse.success(data=slave)
       
    @enginefacade.transactional
    def get_slave_address(self, session, slave_name: str = None, uuid: str = None):
        if uuid:
            addr = db.get_slave_address_by_uuid(session, uuid)
            return APIResponse.success(data=addr)
        else:
            uuid = db.get_slave_uuid_by_name(session, slave_name)
            addr = db.get_slave_address_by_uuid(session, uuid)
            return APIResponse.success(data=addr)
    