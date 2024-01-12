from src.domain_xml.xml_init import create_initial_xml
from src.utils.config import CONF
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
from src.volume.api import API
from src.guest.db import db as db
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.utils.response import APIResponse
from src.network.api import NetworkAPI
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
        data = {"domain_xml":guest.get_xml_string(), "domain_name": domain_name}
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/addDomain/", data=data).json())
        if(response.code == 0):
            uuid = response.get_data()['uuid']
            db.create_guest(session, uuid, domain_name, slave_name, **kwargs)
        return response

    @enginefacade.transactional
    def shutdown_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/shutdownDomain/", data=data).json)
        if(response.code == 0):
            db.status_update(session, uuid, status=status[5])
        return response

    @enginefacade.transactional
    def destroy_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/destroyDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[5])
        return response

    @enginefacade.transactional
    def pause_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/pauseDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[3])
        return response

    @enginefacade.transactional
    def resume_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/resumeDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[1])
        return response

    @enginefacade.transactional
    def start_domain(self, session, domain_name: str, slave_name: str):
        uuid = db.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/startDomain/", data=data).json())
        if(response.code == 0):
            db.status_update(session, uuid, status=status[1])
        return response

    @enginefacade.transactional
    def batch_start_domains(self, session, domains_name_list, slave_name: str):
        data = {"domains_name_list": domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchStartDomains/", data=data).json())
        return response

    @enginefacade.transactional
    def batch_pause_domains(self, session, domains_name_list, slave_name: str):
        data = {"domains_name_list": domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchPauseDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            db.status_update(session, uuid, status[3])
        return response

    @enginefacade.transactional
    def batch_shutdown_domains(self, session, domains_name_list, slave_name: str):
        data = {"domains_name_list": domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchShutdownDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            db.status_update(session, uuid, status[4])
        return response

    @enginefacade.transactional
    def batch_delete_domains(self, session, domains_name_list, slave_name: str):
        data = {"domains_name_list": domains_name_list}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/batchDeleteDomains/", data=data).json())
        success_list = response.get_data()["success"]
        for uuid in success_list:
            db.delete_domain_by_uuid(session, uuid)
        return response

    @enginefacade.transactional
    def batch_restart_domains(self, session, domains_name_list, slave_name: str):
        data = {"domains_name_list": domains_name_list}
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
        data = {"domain_name": domain_name, "new_name": new_name}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/renameDomain/", data=data).json())
        if(response.code == 0):
            uuid = db.get_uuid_by_name(session, domain_name, slave_name)
            db.update_guest(session, uuid, values={"name": new_name})
        return response

    @enginefacade.transactional
    def put_description(self, session, domain_name, new_description, slave_name):
        data = {"domain_name": domain_name, "new_description": new_description}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/putDes/", data=data).json())
        if(response.code == 0):
            uuid = db.get_uuid_by_name(session, domain_name, slave_name)
            db.update_guest(session, uuid, values={"description": new_description})
        return response

    @enginefacade.transactional
    def delete_domain(self, session, domain_name, slave_name):
        data = {"domain_name": domain_name}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/delDomain/", data=data).json())
        if(response.code == 0):
            uuid = db.get_uuid_by_name(session, domain_name, slave_name)
            db.delete_domain_by_uuid(session, uuid = uuid)
        return response
    
    @enginefacade.transactional
    def attach_nic(self, session, domain_name, slave_name, interface_name, flags):
        xml = networkapi.get_interface_xml(interface_name)
        data = {
            "domain_name": domain_name,
            "device_xml": xml,
            "flags": flags
        }
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.code == 0:
            domain_uuid = db.get_uuid_by_name(session, domain_name, slave_name)
            networkapi.attach_interface_to_domain(domain_uuid, interface_name)
        return response
    

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
    