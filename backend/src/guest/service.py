import requests
from src.domain_xml.xml_init import create_initial_xml
from src.utils.config import CONF
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
from src.guest.db import db as guestDB
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.utils.response import APIResponse
from src.network.api import NetworkAPI
from src.domain_xml.device import graphics
from src.domain_xml.device.disk import create_cdrom_builder
from src.volume.api import StorageAPI
from src.utils.generator import UUIDGenerator
from src.domain_xml.domain.guest import Guest as GuestBuilder
import src.utils.generator as generator
from src.guest.db.models import Guest as GuestModel
import src.utils.consts as consts 
from src.utils.websockify.websockify_manager import WebSockifyManager

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

storage_api = StorageAPI()
networkapi = NetworkAPI()
generator =UUIDGenerator()
websockify_manager = WebSockifyManager()

class GuestService():
    @enginefacade.transactional
    def create_domain(self, session, domain_name: str, slave_name: str, **kwargs) -> APIResponse:
        exist_uuids =[]
        for guest in guestDB.get_domain_list(session):
            exist_uuids.append(guest.uuid)
        guest_uuid = generator.get_uuid(exist_uuids)
        guest: GuestBuilder = create_initial_xml(domain_name, guest_uuid)
        response = storage_api.clone_volume("8388ad7f-e58b-4d94-bf41-6e95b23d0d4a", domain_name, guest_uuid, rt_flag=1)
        guest.devices.disk.append(response.get_data()["disk"]) 

        # rbdXML = RbdVolumeXMLBuilder()
        # device = rbdXML.construct(domain_name)
        # guest.devices.disk.append(device)
        # guest.devices.disk.append(create_cdrom_builder(source_path="/home/kvm/images/ubuntu-22.04.3-live-server-arm64.iso", target_dev="sda"))
        url = CONF['slaves'][slave_name]
        xml = {consts.P_DOMAIN_XML : guest.get_xml_string(), consts.P_DOMAIN_NAME : domain_name}
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/addDomain/", data=xml).json())
        if(response.code == 0):
            guestDB.create_guest(session, guest_uuid, domain_name, slave_name, **kwargs)
        return response

    @enginefacade.transactional
    def shutdown_domain(self, session, domain_uuid: str) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/shutdownDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, domain_uuid, status=status[5])
        return response
    
    @enginefacade.transactional
    def get_domain_detail(self, session, domain_uuid: str) -> APIResponse:
        guest = guestDB.get_domain_by_uuid(session, domain_uuid)
        if guest is None:
            return APIResponse(code=400, msg = "domian is None")
        else:
            return APIResponse.success(data=guest.to_dict())

    @enginefacade.transactional
    def destroy_domain(self, session, domain_uuid: str) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/destroyDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, domain_uuid, status=status[5])
        return response

    @enginefacade.transactional
    def pause_domain(self, session, domain_uuid: str) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/pauseDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, domain_uuid, status=status[3])
        return response

    @enginefacade.transactional
    def resume_domain(self, session, domain_uuid: str) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/resumeDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, domain_uuid, status=status[1])
        return response
    
    @enginefacade.transactional
    def reboot_domain(self, session, domain_uuid: str) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/rebootDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, domain_uuid, status=status[1])
        return response

    @enginefacade.transactional
    def start_domain(self, session, domain_uuid: str) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/startDomain/", data=data).json())
        if(response.code == 0):
            guestDB.status_update(session, domain_uuid, status=status[1])
        
        # this invoke is used for juding whether domain interfaces' ip is modified
        # while domain is not running. Related operations would be done within this func
        # networkapi.domain_ip_modified(uuid)    
        
        return response

    def batch_domains_detail(self, domains_uuid_list) -> APIResponse:
        error_list = []
        data = {}
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.get_domain_detail(domain_uuid)
            if response.get_code() == 0:
                data[domain_uuid] = response.get_data()
            else:
                error_list.append(domain_uuid)
        return APIResponse.success(data=data, msg = "error list: " + str(error_list))


    def batch_start_domains(self, domains_uuid_list) -> APIResponse:
        success_list = []
        error_list = []
        msg_list = []
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.start_domain(domain_uuid)
            if response.get_code() == 0:
                success_list.append(domain_uuid)
            else:
                error_list.append(domain_uuid)
                msg_list.append(response.get_msg())
        response = APIResponse()
        if len(error_list) == 0:
            return APIResponse.success()
        else:
            return APIResponse(code = 400, data = {"error_list" : error_list}, msg = str(msg_list))


    def batch_pause_domains(self, domains_uuid_list) -> APIResponse:
        success_list = []
        error_list = []
        msg_list = []
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.pause_domain(domain_uuid)
            if response.get_code() == 0:
                success_list.append(domain_uuid)
            else:
                error_list.append(domain_uuid)
                msg_list.append(response.get_msg())
        response = APIResponse()
        if len(error_list) == 0:
            return APIResponse.success()
        else:
            return APIResponse(code = 400, data = {"error_list" : error_list}, msg = str(msg_list))


    def batch_shutdown_domains(self, domains_uuid_list) -> APIResponse:
        success_list = []
        error_list = []
        msg_list = []
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.shutdown_domain(domain_uuid)
            if response.get_code() == 0:
                success_list.append(domain_uuid)
            else:
                error_list.append(domain_uuid)
                msg_list.append(response.get_msg())
        response = APIResponse()
        if len(error_list) == 0:
            return APIResponse.success()
        else:
            return APIResponse(code = 400, data = {"error_list" : error_list}, msg = str(msg_list))


    def batch_delete_domains(self, domains_uuid_list) -> APIResponse:
        success_list = []
        error_list = []
        msg_list = []
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.delete_domain(domain_uuid)
            if response.get_code() == 0:
                success_list.append(domain_uuid)
            else:
                error_list.append(domain_uuid)
                msg_list.append(response.get_msg())
        response = APIResponse()
        if len(error_list) == 0:
            return APIResponse.success()
        else:
            return APIResponse(code = 400, data = {"error_list" : error_list}, msg = str(msg_list))


    def batch_restart_domains(self, domains_uuid_list) -> APIResponse:
        success_list = []
        error_list = []
        msg_list = []
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.reboot_domain(domain_uuid)
            if response.get_code() == 0:
                success_list.append(domain_uuid)
            else:
                error_list.append(domain_uuid)
                msg_list.append(response.get_msg())
        response = APIResponse()
        if len(error_list) == 0:
            return APIResponse.success()
        else:
            return APIResponse(code = 400, data = {"error_list" : error_list}, msg = str(msg_list))
        
        
    def batch_resume_domains(self, domains_uuid_list) -> APIResponse:
        success_list = []
        error_list = []
        msg_list = []
        for domain_uuid in domains_uuid_list:
            response: APIResponse = self.resume_domain(domain_uuid)
            if response.get_code() == 0:
                success_list.append(domain_uuid)
            else:
                error_list.append(domain_uuid)
                msg_list.append(response.get_msg())
        response = APIResponse()
        if len(error_list) == 0:
            return APIResponse.success()
        else:
            return APIResponse(code = 400, data = {"error_list" : error_list}, msg = str(msg_list))

    def get_domains_list(self) -> APIResponse:
        return guestDB.get_domain_list()

    @enginefacade.transactional
    def rename_domain(self, session, domain_uuid, new_name) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid, consts.P_NEW_NAME : new_name}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/renameDomain/", data=data).json())
        if(response.code == 0):
            guestDB.update_guest(session, domain_uuid, values={"name": new_name})
        return response

    @enginefacade.transactional
    def put_description(self, session, domain_uuid, new_description) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid, consts.P_NEW_DESCRIPTION : new_description}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/putDes/", data=data).json())
        if(response.code == 0):
            guestDB.update_guest(session, domain_uuid, values={"description": new_description})
        return response

    @enginefacade.transactional
    def delete_domain(self, session, domain_uuid, flags) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/delDomain/", data=data).json())
        if(response.code == 0):
            guestDB.delete_domain_by_uuid(session, uuid = domain_uuid)
            volume_list = storage_api.get_all_volumes(guest_uuid=domain_uuid).get_data()
            #删除磁盘
            if(flags == 0):
                for volume in volume_list:
                    storage_api.delete_volume(volume.uuid)
            else:
                for volume in volume_list:
                    storage_api.detach_volume_from_guest(volume.uuid)
        return response
    
    @enginefacade.transactional
    def attach_nic(self, session, domain_uuid, interface_name, flags: int) -> APIResponse:
        
        response = networkapi.attach_interface_to_domain(domain_uuid, interface_name)
        xml = networkapi.get_interface_xml(interface_name).get_data()
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_DEVICE_XML : xml,
            consts.P_FLAGS : flags
        }
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.code != 0:
            networkapi.detach_interface_from_domain(domain_uuid, interface_name)
            return APIResponse.error(code=400, msg=response.msg)
        return response
    
    
    @enginefacade.transactional
    def detach_nic(self, session, domain_uuid, interface_name, flags: int) -> APIResponse:
        xml = networkapi.get_interface_xml(interface_name).get_data()
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_DEVICE_XML : xml,
            consts.P_FLAGS : flags
        }
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/detachDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
        
        response = networkapi.detach_interface_from_domain(domain_uuid, interface_name)
        return response
    
    
    @enginefacade.transactional
    def detach_all_nic_from_domain(self, session, domain_uuid, flags: int=2) -> APIResponse:
        interface_names = networkapi.get_domain_interface_names(domain_uuid).get_data()
        responses: list[APIResponse] = []
        for name in interface_names:
            response =self.detach_nic(session, domain_uuid, name, flags)
            responses.append(response)
        
        for resp in responses:
            if resp.get_code() != 0:
                return APIResponse.error(code=400, msg=f"detach not complete")
        return APIResponse.success()
    
    
    @enginefacade.transactional
    def list_nic(self, session, domain_uuid: str) -> APIResponse:
        return networkapi.list_domain_interfaces(domain_uuid)
    
    
    @enginefacade.transactional
    def set_domain_vcpu(self, session, domain_uuid: str, cpu_num: int, flags: int) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid, consts.P_CPU_NUM : cpu_num, consts.P_FLAGS : flags}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setCPU/", data=data).json())
        if(response.code == 0):
            guestDB.update_guest(session, domain_uuid, values={"cpu": cpu_num})
        return response
    
    @enginefacade.transactional
    def set_domain_memory(self, session, domain_uuid: str, memory_size: int, flags: int) -> APIResponse:
        data = {consts.P_DOMAIN_UUID : domain_uuid, consts.P_MEMORY_SIZE : memory_size, consts.P_FLAGS : flags}
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setMemory", data=data).json())
        if(response.code == 0):
            guestDB.update_guest(session, domain_uuid, values={"memory": memory_size})
        return response
    
    
    @enginefacade.transactional
    def add_vnc(self, session, domain_uuid, port: str, passwd: str, flags: int) -> APIResponse:
        if port:
            port = int(port)
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        url_ip = url.split(':')[0]
        vnc_address = f"{url_ip}:{port}"
        
        if self.is_graphic_address_used(session, vnc_address):
            return APIResponse.error(code=400, msg="port has been used")
        
        xml = graphics.create_vnc_viewer(port, passwd).get_xml_string()
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
         
        address = f"{url_ip}:{port}:{passwd}"
        websockify_config = f"{url_ip}:{port}"
        websockify_manager.update_web_sockify_conf(domain_uuid, websockify_config)
        guestDB.update_guest(session, domain_uuid, values={"vnc_address":address })
        return response
    
    
    @enginefacade.transactional
    def delete_vnc(self, session, domain_uuid, flags: int) -> APIResponse:
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        
        # reset the vnc address to the init value
        xml = graphics.create_local_auto_port_vnc_viewer().get_xml_string()
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
        
        websockify_manager.delete_web_sockify_conf(domain_uuid)
        guestDB.update_guest(session, domain_uuid, values={"vnc_address": None})
        return response
    
    
    @enginefacade.transactional
    def add_spice(self, session, domain_uuid, port: str, passwd: str, flags: int) -> APIResponse:
        if port:
            port = int(port)
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
            
        vnc_address = f"{url}:{port}"
        
        if self.is_graphic_address_used(session, vnc_address):
            return APIResponse.error(code=400, msg="port has been used")
        
        xml = graphics.create_spice_viewer(port, passwd).get_xml_string()
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
        
        address = f"{url}:{port}:{passwd}"
        guestDB.update_guest(session, domain_uuid, values={"spice_address":address })
        return response
    
    
    @enginefacade.transactional
    def change_graphic_passwd(self, session, domain_uuid: str, port:int, passwd: str, flags: int, vnc=True) -> APIResponse:
        if vnc:
            xml = graphics.create_vnc_viewer(port, passwd).get_xml_string()
        else:
            xml = graphics.create_spice_viewer(port, passwd).get_xml_string() 
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_DEVICE_XML: xml,
            consts.P_FLAGS : flags
        }
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateDevice/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
       
        address = f"{url}:{port}:{passwd}"
        if vnc:
            guestDB.update_guest(session, domain_uuid, values={"vnc_address":address })
        else:
            guestDB.update_guest(session, domain_uuid, values={"spice_address":address })
        return response
        
    @enginefacade.transactional    
    def monitor(self, session, domain_uuid: str) -> APIResponse:
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
        }
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/monitor/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
        return response
        
    @enginefacade.transactional    
    def set_user_passwd(self, session, domain_uuid: str, user_name: str, passwd: str) -> APIResponse:
        data = {
            consts.P_DOMAIN_UUID : domain_uuid,
            consts.P_USER_NAME: user_name,
            consts.P_PASSWD: passwd
        }
        slave_name = guestDB.get_domain_slave_name(session, domain_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/setUserPasswd/", data=data).json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
        return response

    @enginefacade.transactional
    def get_domain_slave_name(self, session, domain_uuid: str) -> APIResponse:
        return APIResponse.success(guestDB.get_domain_slave_name(session, domain_uuid))

    @enginefacade.transactional
    def get_domain_status(self, session, domain_uuid: str) -> APIResponse:
        return APIResponse.success(guestDB.get_domain_status(session, domain_uuid))

    @enginefacade.transactional
    def attach_disk_to_guest(self, session,
                             guest_uuid: str,
                             volume_name: str,
                             volume_uuid: str,
                             size: int,
                             flags: int) -> APIResponse:
        response = storage_api.attach_volume_to_guest(guest_uuid, volume_uuid,
                                                      volume_name, size, rt_flag=2)
        if response.is_success():
            xml_string = response.get_data()
        else:
            raise Exception(f'Failed to attach disk, failed to get device XML:'
                            f'{response.get_msg()}')

        data = {
            consts.P_DOMAIN_UUID: guest_uuid,
            consts.P_DEVICE_XML: xml_string,
            consts.P_FLAGS: flags
        }
        slave_name = guestDB.get_domain_slave_name(session, guest_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/attachDevice/", data=data).json())
        if response.is_success():
            return response
        else:
            raise Exception(f'Failed to attach disk: {response.get_msg()}')

    @enginefacade.transactional
    def detach_disk_from_domain(self, session, guest_uuid: str,
                                volume_uuid: str, flags: int) -> APIResponse:
        response = storage_api.get_volume(volume_uuid, rt_flag=2)
        if response.is_success():
            xml_string = response.get_data()
        else:
            raise Exception(f'Failed to detach disk; '
                            f'Failed to get disk xml: {response.get_msg()}')

        data = {
            consts.P_DOMAIN_UUID: guest_uuid,
            consts.P_DEVICE_XML: xml_string,
            consts.P_FLAGS: flags
        }
        slave_name = guestDB.get_domain_slave_name(session, guest_uuid)
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/detachDevice/", data=data).json())
        if response.is_success():
            return storage_api.detach_volume_from_guest(volume_uuid)
        else:
            raise Exception(f'Failed to dettach disk: {response.get_msg()}')

    @enginefacade.transactional
    def post_domain_start(self, session, domain_uuid) -> APIResponse:
        """
        Called after domain start.
        Currently only has static ip init
        """
        networkapi.init_set_domain_static_ip(domain_uuid)

    @enginefacade.transactional
    def post_domain_create(self, session, domain_uuid, network_name: str, interface_name: str) -> APIResponse:
        """
        Called after comain creation. 
        Currently only has interface(nic) attachment

        """
        exists = networkapi.interface_exists(interface_name).get_data()
        # if given interface does not exist, create a new one with random ip
        if not exists:
            networkapi.create_interface(interface_name, network_name, None, None)
        
        networkapi.attach_interface_to_domain(domain_uuid, interface_name)
        
        
    @enginefacade.transactional    
    def is_graphic_address_used(self, session, address: str):
        """
        determine whether a ip:port has been used by other vnc/spice

        """
        guests: list[GuestModel] = guestDB.get_domain_list(session)
        address_list: list[str] = []
        for guest in guests:
            if guest.vnc_address is not None:
                address_list.append(guest.vnc_address)
            if guest.spice_address is not None:
                address_list.append(guest.spice_address)
        
        ip_ports: list[str] = []
        for s in address_list:
            parts = s.split(":")
            ip_port = f"{parts[0]}:{parts[1]}"
            ip_ports.append(ip_port)
        
        return address in ip_ports
        

class SlaveService():
    @enginefacade.transactional
    def create_slave(self, session, slave_address, slave_name) -> APIResponse:
       slave = guestDB.create_slave(session, slave_name, slave_address)
       if slave:
           return APIResponse.success(data=slave.uuid)
      
    @enginefacade.transactional
    def delete_slave(self, session, slave_name) -> APIResponse:
        slave = guestDB.get_slave_by_name(session, slave_name)
        if slave is None:
            return APIResponse.error(code=400, msg=f"Cannot find a slave where name = {slave_name}")
        guestDB.delete_slave(session, slave_name)
        return APIResponse.success()
    
    @enginefacade.transactional
    def slave_detail(self, session, slave_name) -> APIResponse:
        slave = guestDB.get_slave_by_name(session, slave_name)
        if slave is None:
            return APIResponse.error(code=400, msg=f"Cannot find a slave where name = {slave_name}")
        data = slave.to_dict()
        return APIResponse.success(data)
    
    @enginefacade.transactional
    def get_slave_by_uuid(self, session, uuid: str) -> APIResponse:
       slave = guestDB.get_slave_by_uuid(session, uuid)
       return APIResponse.success(data=slave)
   
    @enginefacade.transactional
    def get_slave_by_name(self, session, name: str) -> APIResponse:
       slave = guestDB.get_slave_by_name(session, name)
       return APIResponse.success(data=slave)
       
    @enginefacade.transactional
    def get_slave_address(self, session, slave_name = None, uuid: str = None) -> APIResponse:
        if uuid:
            addr = guestDB.get_slave_address_by_uuid(session, uuid)
            return APIResponse.success(data=addr)
        else:
            uuid = guestDB.get_slave_uuid_by_name(session, slave_name)
            addr = guestDB.get_slave_address_by_uuid(session, uuid)
            return APIResponse.success(data=addr)
      
    @enginefacade.transactional
    def get_slave_guests(self, session, name: str) -> APIResponse:
       guests = guestDB.get_slave_guests(session, name)
       data = [guest.uuid for guest in guests]
       return APIResponse.success(data=data)
   
    @enginefacade.transactional
    def init_slave_db(self, session) -> APIResponse:
        slaves = CONF['slaves']
        res = []
        for key, value in slaves.items():
            slave_name = key
            slave_addr = value
            create_res =self.create_slave(session, slave_name, slave_addr).get_data()
            res.append(create_res)
        return APIResponse.success(data=res) 
    
    
    def get_slave_status(self, slave_name) -> APIResponse:
        url = CONF['slaves'][slave_name]
        response: APIResponse = APIResponse().deserialize_response(requests.get(url="http://"+url+"/getSystemInfo/").json())
        if response.code != 0:
            return APIResponse.error(code=400, msg=response.msg)
        
        return response
    
    
    def get_all_slave_status(self) -> APIResponse:
        slaves = CONF['slaves']
        res = []
        for key, value in slaves.items():
            slave_name = key
            url = value
            data = APIResponse().deserialize_response(requests.get(url="http://"+url+"/getSystemInfo/").json()).get_data()
            res.append(data)
        return APIResponse.success(data)
            
    
