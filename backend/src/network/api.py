from src.network.service import NetworkService
from src.utils.response import APIResponse

network_service = NetworkService()
class NetworkAPI():
    
    def create_top_network(network_address: str):
        return network_service.create_top_network(network_address=network_address)
    
    def create_interface(self,
                         name: str,
                         network_name: str,
                         ip_address: str,
                         mac: str = None,
                         inerface_type: str = "direct") -> APIResponse:
        return network_service.create_interface(name=name,
                                                network_name=network_name,
                                                ip_address=ip_address,
                                                mac=mac,
                                                inerface_type=inerface_type)
    
    def delete_interface(self, interface_uuid: str, name: str=None) -> APIResponse:
        return network_service.delete_interface(interface_uuid=interface_uuid,
                                                name=name)
    
    def create_network(self, name, network_address) -> APIResponse:
        return network_service.create_network(name=name,
                                              ip_address=network_address)
    
    def delete_network(self, name) -> APIResponse:
        return network_service.delete_network(name=name)
    
    
    def get_interface_xml(self, interface_name) -> APIResponse:
        return network_service.get_interface_xml(interface_name)
    
    
    def attach_interface_to_domain(self, domain_uuid: str, interface_name: str)-> APIResponse:
        return network_service.add_interface_to_domain(interface_name=interface_name,
                                                       domain_uuid=domain_uuid)
    
    def detach_interface_from_domain(self, domain_uuid: str, interface_name: str)-> APIResponse:
        return network_service.remove_interface_from_domain(interface_name=interface_name,
                                                       domain_uuid=domain_uuid)
    
        
    def list_networks(self) -> APIResponse:
        return network_service.list_networks()
    
    
    def list_interfaces(self) -> APIResponse:
        return network_service.list_interfaces()
    
    
    def network_detail(self, network_name: str) -> APIResponse:
        return network_service.network_detail(network_name)
    
    
    def interface_detail(self, interface_name: str) -> APIResponse:
        return network_service.interface_detail(interface_name)