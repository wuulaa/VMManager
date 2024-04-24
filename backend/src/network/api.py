from src.network.service import NetworkService
from src.utils.response import APIResponse
from src.utils.singleton import singleton

network_service = NetworkService()

@singleton
class NetworkAPI():
    
    def create_top_network(self, network_address: str) -> APIResponse:
        return network_service.create_top_network(network_address=network_address)
    
    def delete_top_network(self, network_address: str) -> APIResponse:
        return network_service.delete_top_network(network_address=network_address)
    
    def create_interface(self,
                         name: str,
                         network_name: str,
                         ip_address: str,
                         gateway: str, 
                         mac: str = None,
                         inerface_type: str = "direct") -> APIResponse:
        return network_service.create_interface(interface_name=name,
                                                network_name=network_name,
                                                ip_address=ip_address,
                                                gateway=gateway,
                                                mac=mac,
                                                inerface_type=inerface_type)
    
    def delete_interface(self, interface_name: str) -> APIResponse:
        return network_service.delete_interface(interface_name=interface_name)
    
    def interface_exists(self, interface_name: str)-> APIResponse:
        return network_service.interface_exists(interface_name=interface_name)
    
    def clone_interface(self, interface_name: str, new_name: str, new_ip: str) -> APIResponse:
        return network_service.clone_interface(interface_uuid=None, interface_name=interface_name,new_name=new_name, new_ip=new_ip)
    
    
    def modify_interface(self, interface_name: str, ip_addr: str, gateway:str) -> APIResponse:
        return network_service.modify_interface(interface_uuid=None, interface_name=interface_name,
                                                ip_addr=ip_addr, gateway=gateway)
    
    
    def create_network(self, name, network_address) -> APIResponse:
        return network_service.create_network(name,
                                              network_address)
        
    def reload_network(self) -> APIResponse:
        return network_service.reload_network()
    
    def delete_network(self, name) -> APIResponse:
        return network_service.delete_network(network_name=name)
    
    
    def get_interface_xml(self, interface_name) -> APIResponse:
        return network_service.get_interface_xml(interface_name=interface_name)
    
    
    def attach_interface_to_domain(self, domain_uuid: str, interface_name: str)-> APIResponse:
        return network_service.add_interface_to_domain(interface_name=interface_name,
                                                       domain_uuid=domain_uuid)
    
    def detach_interface_from_domain(self, domain_uuid: str, interface_name: str)-> APIResponse:
        return network_service.remove_interface_from_domain(interface_name=interface_name,
                                                       domain_uuid=domain_uuid)
    
    
    def init_set_domain_static_ip(self, domain_uuid)->APIResponse:
        return network_service.init_set_domain_static_ip(domain_uuid=domain_uuid)
    
    
    def update_domain_veth_name(self, domain_uuid)->APIResponse:
        return network_service.update_domain_veth_name(domain_uuid=domain_uuid)
    
        
    def list_networks(self, user_name) -> APIResponse:
        return network_service.list_networks(user_name=user_name)
    
    
    def list_interfaces(self, user_name) -> APIResponse:
        return network_service.list_interfaces(user_name=user_name)
    
    
    def list_domain_interfaces(self, domain_uuid)-> APIResponse:
        return network_service.list_domain_interfaces(domain_uuid=domain_uuid)
    
    
    def network_detail(self, network_name: str) -> APIResponse:
        return network_service.network_detail(network_name)
    
    
    def interface_detail(self, interface_name: str) -> APIResponse:
        return network_service.interface_detail(interface_name)
    
    
    def get_domain_interface_names(self, domain_uuid: str) -> APIResponse:
        return network_service.get_domain_interface_names(domain_uuid=domain_uuid)
    

    def get_network_user_uuid(self, network_name) -> APIResponse:
        return network_service.get_network_user_uuid(network_name=network_name)
    
   
    def get_interface_user_uuid(self, interface_name) -> APIResponse:
        return network_service.get_interface_user_uuid(interface_name=interface_name)