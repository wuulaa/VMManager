import docker
import docker.errors
import docker.models
import docker.models.networks
from docker.models.networks import Network
import docker.types
from docker.models.containers import Container
import subprocess
from src.utils.response import APIResponse


class DockerOvs:
    """
    Currently a useless class because if use ovs as the network bridge,
    docker containers would not be able to use port mapping.
    """
    def add_port(slef,
                 bridge:str,
                 interface:str,
                 container_id: str,
                 ip_address:str,
                 gateway:str,
                 ):
        command = f"ovs-docker add-port {bridge} {interface} {container_id} --ipaddress={ip_address} --gateway={gateway}"
        res = subprocess.run(command, shell=True)
        if res.stderr:
            return APIResponse.error(code=400, msg=res.stderr)
        return APIResponse.success()
        
    def del_port(self,
                 bridge:str,
                 interface:str,
                 container_id:str):
        command = f"ovs-docker del-port {bridge} {interface} {container_id}"
        res = subprocess.run(command, shell=True)
        if res.stderr:
            return APIResponse.error(code=400, msg=res.stderr)
        return APIResponse.success()



class DockerManager:
    
    def __init__(self, client:docker.DockerClient = None):
        if client is None:
            client = docker.from_env()
        self.client : docker.DockerClient = client
        
    
    def pull_image(self, repository:str, tag:str):
        try:
            self.client.images.pull(repository, tag=tag)
            return APIResponse.success()
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    #############
    # container #
    #############
        
    def run_container(self, image:str,
                      name: str=None,
                      cpu_count: int=None,
                      memory_limit: str=None,
                      network: str=None,
                      ports:dict=None,
                      detach = True
                      ):
        try:
            if network is None:
                network = "none"
            container: Container = self.client.containers.run(image,
                                    name=name,
                                    cpu_count=cpu_count,
                                    mem_limit=memory_limit,
                                    network=network,
                                    ports=ports,
                                    detach=detach
                                    )
            return APIResponse.success(container.id)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    def create_container(self, image:str,
                         name: str=None,
                         cpu_shares: int=None,
                         memory_limit: str=None,
                         network: str=None,
                         ports:dict=None,
                         detach = True):
        try:
            if network is None:
                network = "none"
            container = self.client.containers.create(image,
                                                    name=name,
                                                    cpu_shares=cpu_shares,
                                                    mem_limit=memory_limit,
                                                    network=network,
                                                    ports=ports,
                                                    detach=detach
                                                    )
            return APIResponse.success(container.id)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    def _get_container(self, container_id):
        try:
            container: Container = self.client.containers.get(container_id)
            return container
        except Exception as e:
            raise e
        
    def get_container(self, container_id):
        try:
            container: Container = self.client.containers.get(container_id)
            return APIResponse.success(container.id)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    def start_container(self, container_id):
        try:
            container = self._get_container(container_id)
            if container is not None:
                container.start()
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
            
    
    def restart_container(self, container_id):
        try:
            container = self._get_container(container_id)
            if container is not None:
                container.restart()
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    def stop_container(self, container_id):
        try:
            container = self._get_container(container_id)
            if container is not None:
                container.stop()
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    def remove_container(self, container_id, remove_volume: bool=False):
        try:
            container = self._get_container(container_id)
            if container is not None:
                container.remove(v=remove_volume)
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    def pause_container(self, container_id):
        try:
            container = self._get_container(container_id)
            if container is not None:
                container.pause()
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    def unpause_container(self, container_id):
        try:
            container = self._get_container(container_id)
            if container is not None:
                container.unpause()
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
            
    def update_container(self, container_id, mem_limit: str=None, cpu_shares:int=None, new_name:str=None):
        try:
            container = self._get_container(container_id)
            if container is not None:
                if new_name is not None:
                    container.rename(new_name)
                if mem_limit is not None:
                    container.update(mem_limit=mem_limit)
                if cpu_shares is not None:
                    container.update(cpu_shares=cpu_shares)
                return APIResponse.success(container.id)
            return APIResponse.error(code=404, msg="container not found")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    #############
    #   swarm   #
    #############
    
    def init_swarm(self, name:str=None, advertise_addr:str=None,
                   listen_addr: str="0.0.0.0:2377",
                   default_addr_pool: list=None):
        try:
            res = self.client.swarm.init(name=name,
                                advertise_addr=advertise_addr,
                                listen_addr=listen_addr,
                                default_addr_pool=default_addr_pool
                                )
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    def join_swarm(self, remote_addrs:list, join_token:str,
                   advertise_addr:str=None, listen_addr: str="0.0.0.0:2377"):
        try:
            res = self.client.swarm.join(join_token=join_token,remote_addrs=remote_addrs, advertise_addr=advertise_addr,listen_addr=listen_addr)
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))    
        
        
    def leave_swarm(self, force=False):
        try:
            res = self.client.swarm.leave(force=force)
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e)) 
        
        
    def get_swarm_worker_token(self):
        """
        This function should better be called in a manager node
        """
        try:
            res = self.client.swarm.attrs["JoinTokens"]["Worker"]
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    def get_swarm_manager_token(self):
        """
        This function should better be called in a manager node
        """
        try:
            res = self.client.swarm.attrs["JoinTokens"]["Manager"]
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    #############
    #  network  #
    #############
    
    def crate_network(self, 
                      name:str,
                      subnet:str,
                      gateway:str,
                      driver:str='overlay',
                      attachable=True):
        """
        create a network, default use overlay driver
        return its id
        """
        try:
            ipam_pool = docker.types.IPAMPool(subnet=subnet,
                                            gateway=gateway)
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            network:Network =self.client.networks.create(name, driver=driver,ipam=ipam_config,attachable=attachable)
            return APIResponse.success(network.id)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    def delete_network(self, name:str, id:str=None):
        try:
            if id is not None:
                network:Network = self.client.networks.list(ids=id)[0]
            else:
                network:Network = self.client.networks.list(names=name)[0]
            
            if network:
                network.remove()
            return APIResponse.success(network.id)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    def _get_network(self, name:str, id:str=None):
        try:
            if id is not None:
                network:Network = self.client.networks.list(ids=id)[0]
            else:
                network:Network = self.client.networks.list(names=name)[0]
            
            if network:
                return network
        except Exception as e:
            raise e
        
    
    def connect_container_to_network(self, container_identifier:str, network_name:str, ipv4_address:str=None):
        """
        note that before connecting a container to a network, a
        it's recommended to disconnect it from the old network.
        make sure to disconnect if it was connected to the none network
        """
        try:
            network: Network = self._get_network(network_name)
            container = self._get_container(container_identifier)
            if network is not None and container is not None:
                network.connect(container_identifier, ipv4_address=ipv4_address)
                return APIResponse.success()
            else:
                return APIResponse.error(code=404, msg="wrong container/network name")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    def disconnect_container_to_network(self, container_identifier:str, network_name:str, force=False):
        try:
            network: Network = self._get_network(network_name)
            container = self._get_container(container_identifier)
            if network is not None and container is not None:
                network.disconnect(container_identifier, force=force)
                return APIResponse.success()
            else:
                return APIResponse.error(code=404, msg="wrong container/network name")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    def list_network_containers(self, network_name:str):
        try:
            network: Network = self._get_network(network_name)
            if network is not None:
                containers:list[Container] = network.containers
                res = [container.id for container in containers]
                return APIResponse.success(res)
            else:
                return APIResponse.error(code=404, msg="wrong network name")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    