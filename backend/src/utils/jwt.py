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
    user_api = UserAPI()
    network_api = NetworkAPI()
    
    
    if model == Network:
        network_user_uuid = network_api.get_network_user_uuid(network_name=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return network_user_uuid == current_user_uuid
    
    if model == Interface:
        interface_user_uuid = network_api.get_interface_user_uuid(interface_name=identifier).get_data()
        current_user_uuid = user_api.get_current_user_uuid().get_data()
        return interface_user_uuid == current_user_uuid
