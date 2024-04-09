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
    from src.network.api import NetworkAPI
    from src.network.db.models import Network, Interface
    from src.guest.db.models import Guest
    from src.guest.api import GuestAPI
    from src.volume.db.models import Volume, Pool
    from src.volume.api import StorageAPI
    
    user_api = UserAPI()
    network_api = NetworkAPI()
    guest_api = GuestAPI()
    storage_api = StorageAPI()
    
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
    
    return False
    
