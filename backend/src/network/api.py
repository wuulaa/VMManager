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