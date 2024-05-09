from src.docker.service import DockerGuestService
from src.utils.response import APIResponse
docker_serice = DockerGuestService()


class DockerAPI:
    def get_slave_name(self, container_uuid: str) -> APIResponse:
        return docker_serice.get_slave_name(container_uuid=container_uuid)
    
    def get_container_id(self, container_uuid: str) -> APIResponse:
        return docker_serice.get_container_id(container_uuid=container_uuid)
    
    
    def create_docker_guest(self,
                            guest_name:str,
                            slave_name:str,
                            vnc_ipport: str,
                            vnc_passwd: str,
                            cpu_share: int= 1024,
                            mem_limit:int = "1024m"
                            ) -> APIResponse:
        return docker_serice.create_docker_guest(guest_name=guest_name,
                                          slave_name=slave_name,
                                          vnc_ipport=vnc_ipport,
                                          vnc_passwd=vnc_passwd,
                                          cpu_share=cpu_share,
                                          mem_limit=mem_limit)
    
    
    def delete_docker_guest(self, container_uuid:str) -> APIResponse:
        return docker_serice.delete_docker_guest(container_uuid=container_uuid)
        
    
    def start_docker_guest(self, container_uuid) -> APIResponse:
        return docker_serice.start_docker_guest(container_uuid=container_uuid)
    

    def stop_docker_guest(self, container_uuid) -> APIResponse:
        return docker_serice.stop_docker_guest(container_uuid=container_uuid)
    

    def restart_docker_guest(self, container_uuid) -> APIResponse:
        return docker_serice.restart_docker_guest(container_uuid=container_uuid)
    
    
    def pause_docker_guest(self, container_uuid) -> APIResponse:
        return docker_serice.pause_docker_guest(container_uuid=container_uuid)
    
    
    def unpause_docker_guest(self, container_uuid) -> APIResponse:
        return docker_serice.unpause_docker_guest(container_uuid=container_uuid)
    
    
    def list_docker_guests(self, user_name=None) -> APIResponse:
        return docker_serice.list_docker_guests(user_name=user_name)
    
    
    def docker_guests_detail(self, container_uuid) -> APIResponse:
        return docker_serice.docker_guests_detail(container_uuid=container_uuid)
        
    
    def rename_docker_guest(self, container_uuid, new_name) -> APIResponse:
        return docker_serice.rename_docker_guest(container_uuid=container_uuid,
                                                 new_name=new_name)
    
    
    def set_docker_guest_cpu_share(self, container_uuid, cpu_shares) -> APIResponse:
        return docker_serice.set_docker_guest_cpu_share(container_uuid=container_uuid,
                                                        cpu_shares=cpu_shares)
    
    
    def set_docker_guest_memory(self, container_uuid, memory_limit) -> APIResponse: 
        return docker_serice.set_docker_guest_memory(container_uuid=container_uuid,
                                                     memory_limit=memory_limit)
    
    
    def attach_docker_nic(self,
                          container_uuid:str,
                          interface_name:str) -> APIResponse:
        return docker_serice.attach_docker_nic(container_uuid=container_uuid,
                                               interface_name=interface_name)
    
    
    def detach_docker_nic(self,
                          interface_name:str) -> APIResponse:
        return docker_serice.detach_docker_nic(interface_name=interface_name)
    
    
    def monitor(self):
        pass
    
    
    def get_user_uuid(self, container_uuid) -> APIResponse:
        return docker_serice.get_user_uuid(container_uuid=container_uuid)
    
    
    def get_user_name(self, container_uuid) -> APIResponse:
        return docker_serice.get_user_name(container_uuid=container_uuid)
    

