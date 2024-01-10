from src.domain_xml.xml_init import create_initial_xml
from src.utils.config import CONF
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
from src.volume.api import API
from src.guest.service import GuestService
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.utils.response import APIResponse
import requests
import json

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
guestService = GuestService()
vol_api = API()

@singleton
class GuestAPI():

    @enginefacade.transactional
    def create_domain(self, domain_name: str, slave_name: str, **kwargs):
        guest = create_initial_xml(domain_name)
        vol_api.create_volume("a2d6b10a-8957-4648-8052-8371fb10f4e1", domain_name, 20*1024)
        rbdXML = RbdVolumeXMLBuilder()
        device = rbdXML.construct(domain_name)
        guest.devices.disk.append(device)
        url = CONF['slaves'][slave_name]
        data = {"domain_xml":guest.get_xml_string(), "domain_name": domain_name}
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/addDomain/", data=data))
        if(response.code == 0):
            uuid = response.get_data()['uuid']
            guestService.create_guest(uuid, domain_name, slave_name, **kwargs)
        return response

    @enginefacade.transactional
    def shutdown_domain(self, domain_name: str, slave_name: str):
        uuid = guestService.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/shutdownDomain/", data=data))
        if(response.code == 0):
            guestService.status_update(uuid, status=status[5])
        return response

    @enginefacade.transactional
    def destroy_domain(self, domain_name: str, slave_name: str):
        uuid = guestService.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/destroyDomain/", data=data))
        if(response.code == 0):
            guestService.status_update(uuid, status=status[5])
        return response
    
    @enginefacade.transactional
    def pause_domain(self, domain_name: str, slave_name: str):
        uuid = guestService.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/pauseDomain/", data=data))
        if(response.code == 0):
            guestService.status_update(uuid, status=status[3])
        return response
    
    @enginefacade.transactional
    def resume_domain(self, domain_name: str, slave_name: str):
        uuid = guestService.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/resumeDomain/", data=data))
        if(response.code == 0):
            guestService.status_update(uuid, status=status[1])
        return response

    @enginefacade.transactional
    def start_domain(self, domain_name: str, slave_name: str):
        uuid = guestService.get_uuid_by_name(domain_name, slave_name)
        data = {"uuid": uuid}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/startDomain/", data=data))
        if(response.code == 0):
            guestService.status_update(uuid, status=status[1])
        return response

    @enginefacade.transactional
    def get_domains_list():
        return guestService.get_domain_list()

    @enginefacade.transactional
    def rename_domain(self, domain_name, new_name, slave_name):
        data = {"domain_name": domain_name, "new_name": new_name}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/renameDomain/", data=data))
        if(response.code == 0):
            uuid = guestService.get_uuid_by_name(domain_name, slave_name)
            guestService.update_guest(uuid, values={"name": new_name})
        return response

    @enginefacade.transactional
    def put_description(self, domain_name, new_description, slave_name):
        data = {"domain_name": domain_name, "new_description": new_description}
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/putDes/", data=data))
        if(response.code == 0):
            uuid = guestService.get_uuid_by_name(domain_name, slave_name)
            guestService.update_guest(uuid, values={"description": new_description})
        return response
    
    @enginefacade.transactional
    def delete_domain(self, domain_name, slave_name):
        data = {"domain_name": domain_name}
        url = CONF['slave'][slave_name]
        response: APIResponse = APIResponse(requests.post(url="http://"+url+"/delDomain/", data=data))
        if(response.code == 0):
            uuid = guestService.get_uuid_by_name(domain_name, slave_name)
            guestService.delete_domain_by_uuid(uuid = uuid)
        return response
    



    