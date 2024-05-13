from src.common.docker_manager.docker_manager import DockerManager
from src.docker.db.models import DockerGuest
from src.utils.config import CONF
from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.utils.response import APIResponse
from src.utils.generator import UUIDGenerator
import src.utils.consts as consts 
from src.utils.jwt import check_user
from src.user.api import UserAPI
from src.user.db.models import User
from src.docker.db import db
import requests
import src.utils.port as NetPort

user_api = UserAPI()

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

@singleton
class DockerGuestService:
     
    @enginefacade.transactional
    def create_docker_guest(self, session,
                            guest_name:str,
                            slave_name:str,
                            vnc_ipport: str,
                            vnc_passwd: str,
                            cpu_share: int= 1024,
                            mem_limit:int = "1024m"
                            ):
        try:
            # 1. check user
            user_uuid = user_api.get_current_user_uuid().get_data()
            if user_uuid is None:
                return APIResponse.error(code = 400, msg = 'user_uuid is None.')
            
            slave_url = CONF['slaves'][slave_name]
            slave_ip = slave_url.split(':')[0]
            image = CONF['docker']['desktop_image']
     
            
            # 2. handle vnc
            # vnc_address eg: 127.0.0.1:5080
            # docker 修改端口映射很麻烦，因此在创建容器时就设置好vnc对外的端口映射
            # 包括vnc密码
            # 暂且省略websockify的部分
            if vnc_ipport is None:
                vnc_ipport = self.find_first_avaliable_address(session, slave_ip)
            elif self.is_graphic_address_used(session, vnc_ipport):
                vnc_ipport = self.find_first_avaliable_address(session, slave_ip)
            vnc_port = vnc_ipport.split(':')[1]
            
            if vnc_passwd is None:
                vnc_passwd = "123456"
            
            db_vnc_address_passwd = vnc_ipport + ":" + vnc_passwd
            
            # 3. send data to salve
            data = {
                consts.P_IMAGE: image,
                consts.P_CPU_SHARES: cpu_share,
                consts.P_MEMORY: mem_limit,
                consts.P_CONTAINER_NAME: guest_name,
                consts.P_PORTS: str({80: int(vnc_port)})
            }
            
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+slave_url+"/createContainer/", data=data).json())
            
            # 4. handle slave response
            if response.is_success():
                container_id = response.get_data()
                con = db.create_docker_guest(session, None, container_id, guest_name,
                                    user_uuid, slave_name, vnc_address=db_vnc_address_passwd, )
                
            return APIResponse.success(con.uuid)
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def delete_docker_guest(self, session, container_uuid:str):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "shutoff":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/deleteContainer/", data=data).json())
            if response.success():
                # TODO: detach interface
                db.delete_docker_guest_by_uuid(session, container_uuid)
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
    
    @enginefacade.transactional
    def start_docker_guest(self, session, container_uuid):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "shutoff":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/startContainer/", data=data).json())
            if response.success():
                db.status_update(session, container_uuid, 'running')
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def stop_docker_guest(self, session, container_uuid):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "running":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/stopContainer/", data=data).json())
            if response.success():
                db.status_update(session, container_uuid, 'shutoff')
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def restart_docker_guest(self, session, container_uuid):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "running":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/restartContainer/", data=data).json())
            if response.success():
                pass
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def pause_docker_guest(self, session, container_uuid):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "running":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/pauseContainer/", data=data).json())
            if response.success():
                db.status_update(session, container_uuid, 'paused')
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def unpause_docker_guest(self, session, container_uuid):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "paused":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/unpauseContainer/", data=data).json())
            if response.success():
                db.status_update(session, container_uuid, 'running')
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def list_docker_guests(self, session, user_name=None):
        # if not check_user(user_name, User):
        #     return APIResponse.error(code = 400, msg="user_uuid error")
        # if user_name is None:
        #     return APIResponse.success(guestDB.get_domain_list())
        # else:
        #     user_uuid = user_api.get_current_user_uuid().get_data()
        #     return APIResponse.success(guestDB.get_domain_list(user_uuid=user_uuid))
        try:
            container_list:list[DockerGuest] = db.get_docker_guest_list(session)
            res = []
            for container in container_list:
                res.append(container.to_dict())
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def docker_guests_detail(self, session, container_uuid):
        try:
            container = db.get_docker_guest_by_uuid(session, container_uuid)
            return APIResponse.success(container.to_dict())
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
    
    @enginefacade.transactional
    def rename_docker_guest(self, session, container_uuid, new_name):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "shutoff":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id,
                consts.P_CONTAINER_NAME: new_name
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateContainer/", data=data).json())
            if response.success():
                db.update_guest(session, container_uuid, values = {"name": new_name})
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def set_docker_guest_cpu_share(self, session, container_uuid, cpu_shares):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "shutoff":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id,
                consts.P_CPU_SHARES: cpu_shares
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateContainer/", data=data).json())
            if response.success():
                db.update_guest(session, container_uuid, values = {"cpu_shares": cpu_shares})
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def set_docker_guest_memory(self, session, container_uuid, memory_limit):
        try:
            container_status = db.get_docker_guest_status(session, container_uuid=container_uuid)
            if container_status != "shutoff":
                return APIResponse.error(code=401, msg="wrong container status")
            container_id = db.get_docker_guest_by_uuid(session, container_uuid).container_id
            slave_name = db.get_docker_guest_slave_name(session, container_uuid)
            url = CONF['slaves'][slave_name]
            data = {
                consts.P_CONTAINER_ID: container_id,
                consts.P_MEMORY_SIZE: memory_limit 
            }
            response: APIResponse = APIResponse().deserialize_response(requests.post(url="http://"+url+"/updateContainer/", data=data).json())
            if response.success():
                db.update_guest(session, container_uuid, values = {"memory_limit": memory_limit})
            return response
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def attach_docker_nic(self, session,
                          container_uuid:str,
                          interface_name:str):
        from src.network.api import DockerNetworkAPI
        docker_network_api = DockerNetworkAPI()
        try:
            res = docker_network_api.attach_interface_to_container(container_uuid, interface_name)
            return res
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def detach_docker_nic(self, session,
                          interface_name:str):
        from src.network.api import DockerNetworkAPI
        docker_network_api = DockerNetworkAPI()
        try:
            res = docker_network_api.detach_interface_from_container(interface_name)
            return res
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def monitor(self, session):
        pass
    
    
    @enginefacade.transactional
    def get_user_uuid(self, session, container_uuid):
        try:
            return APIResponse.success(db.get_docker_guest_by_uuid(session, container_uuid).user_uuid)
        except Exception as e:
            return APIResponse.error(code = 400, msg=str(e))
    
    
    @enginefacade.transactional
    def get_user_name(self, session, container_uuid):
        try:
            user_uuid = db.get_docker_guest_by_uuid(session, container_uuid).user_uuid
            user_name = user_api.get_user_name_by_uuid(user_uuid)
            return APIResponse.success(user_name)
        except Exception as e:
            return APIResponse.error(code = 400, msg=str(e))
    
    
    @enginefacade.transactional
    def get_slave_name(self, session, container_uuid:str):
        try:
            name = db.get_docker_guest_slave_name(session, container_uuid)
            return APIResponse.success(name)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    @enginefacade.transactional
    def get_container_id(self, session, container_uuid:str):
        try:
            container:DockerGuest = db.get_docker_guest_by_uuid(session, container_uuid)
            return APIResponse.success(container.container_id)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    


    ####################
    # helper functions #
    ####################
    
    @enginefacade.transactional    
    def find_first_avaliable_address(self, session, ip: str, start_port:int=16000, max_attempts:int=200):
        """
        find the first avaliable vnc/spice address 
        """
        from src.guest.db.models import Guest
        from src.guest.db import db as guestdb
        guests: list[Guest] = guestdb.get_domain_list(session)
        containers: list[DockerGuest] = db.get_docker_guest_list(session)
        address_list: list[str] = []
        for guest in guests:
            if guest.vnc_address is not None:
                address_list.append(guest.vnc_address)
            if guest.spice_address is not None:
                address_list.append(guest.spice_address)
        for container in containers:
            if container.vnc_address is not None:
                address_list.append(container.vnc_address)
        
        ip_ports: list[str] = []
        for s in address_list:
            parts = s.split(":")
            ip_port = f"{parts[0]}:{parts[1]}"
            ip_ports.append(ip_port)
            
        for port in range(start_port, start_port + max_attempts):
            address = f"{ip}:{port}"
            if address in ip_ports:
                continue
            if NetPort.is_port_in_use(ip, port):
                continue
            return address
        raise RuntimeError("Unable to find an available port.")
    
    
    @enginefacade.transactional    
    def is_graphic_address_used(self, session, address: str):
        from src.guest.db.models import Guest
        from src.guest.db import db as guestdb
        guests: list[Guest] = guestdb.get_domain_list(session)
        containers: list[DockerGuest] = db.get_docker_guest_list(session)
        address_list: list[str] = []
        for guest in guests:
            if guest.vnc_address is not None:
                address_list.append(guest.vnc_address)
            if guest.spice_address is not None:
                address_list.append(guest.spice_address)
        for container in containers:
            if container.vnc_address is not None:
                address_list.append(container.vnc_address)
        
        ip_ports: list[str] = []
        for s in address_list:
            parts = s.split(":")
            ip_port = f"{parts[0]}:{parts[1]}"
            ip_ports.append(ip_port)
            
        return address in ip_ports