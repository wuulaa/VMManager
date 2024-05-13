from flask import g
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from functools import wraps

def jwt_set_user(func):
    """
    decorator for saving current jwt user
    add above bp functions
    """
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kw):
        
        user = get_jwt_identity()
        g.setdefault("user", user)
        res = func(*args, **kw)
        
        return res
    
    return wrapper



def check_user(identifier:str, model):
    from src.user.api import UserAPI
    from src.network.api import NetworkAPI, DockerNetworkAPI
    from src.network.db.models import Network, Interface
    from src.guest.db.models import Guest
    from src.guest.api import GuestAPI
    from src.volume.db.models import Volume, Pool
    from src.volume.api import StorageAPI
    from src.user.db.models import User
    from src.docker.db.models import DockerGuest
    from src.docker.api import DockerAPI
    
    user_api = UserAPI()
    network_api = NetworkAPI()
    docekr_network_api = DockerNetworkAPI()
    guest_api = GuestAPI()
    storage_api = StorageAPI()
    docker_api = DockerAPI()
    
    if user_api.is_current_user_admin().get_data():
        return True
    
    if model == Network:
        network_user_uuid = network_api.get_network_user_uuid(network_name=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return network_user_uuid == current_user_uuid
    
    if model == Interface:
        interface_user_uuid = network_api.get_interface_user_uuid(interface_name=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return interface_user_uuid == current_user_uuid
    
    if model == Guest:
        guest_user_uuid = guest_api.get_guest_user_uuid(domain_uuid = identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return guest_user_uuid == current_user_uuid
    
    if model == Pool:
        pool_user_uuid = storage_api.get_pool_user_uuid(pool_uuid=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return pool_user_uuid == current_user_uuid
    
    if model == Volume:
        volume_user_uuid = storage_api.get_volume_user_uuid(volume_uuid=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return volume_user_uuid == current_user_uuid
    
    if model == DockerGuest:
        guest_user_uuid = docker_api.get_user_uuid(container_uuid=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return guest_user_uuid == current_user_uuid
    
    if model == User:
        current_user_name = user_api.get_current_user_name().get_data()
        return current_user_name == identifier or user_api.is_current_user_admin().get_data() == True
    
    return False
    
