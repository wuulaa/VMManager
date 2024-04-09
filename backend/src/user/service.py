from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.user.db.models import User
from src.utils.response import APIResponse
import src.user.db.api as db
import hashlib
from src.utils.config import CONF
from flask import jsonify
from flask_jwt_extended import create_access_token
import datetime
from flask import g
from flask_jwt_extended import get_jwt_identity
from src.volume.api import StorageAPI

storage_api = StorageAPI()


@singleton
class UserService:
    
    @enginefacade.transactional
    def login(self, session, username, passwd):
        try:
            # check user and password
            user: User = db.get_user_by_name(username)
            if user is None:
                return APIResponse.error(code=402, msg="user does not exist")
            
            password = encrypt_passwd(passwd)
            if user.password != password:
                return APIResponse.error(code=403, msg="wrong password")
            
            # generate token
            expire_time_string = CONF["jwt"]["expire_time"]
            expire_times = expire_time_string.split(':')
            expire_time = datetime.timedelta(days=float(expire_times[0]),
                                            hours=float(expire_times[1]),
                                            minutes=float(expire_times[2]),
                                            seconds=float(expire_times[3]))
            additional_claims = {"uuid": user.uuid}
            access_token = create_access_token(identity=username,
                                            additional_claims=additional_claims,
                                            expires_delta=expire_time)
            
            # store token in db (is this necessary?)
            db.update_user_token(session, user.uuid, access_token)
            db.update_user_state(session, user.uuid, 'online')
            return APIResponse.success(access_token)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    @enginefacade.transactional
    def logout(self, session, username):
        """
        to log out, frontend should delete its stored cookie.
        backend only updates db
        """
        try:
            user: User = db.get_user_by_name(username)
            if user is None:
                return APIResponse.error(code=402, msg="user does not exist")
            db.update_user_token(session, user.uuid, None)
            db.update_user_state(session, user.uuid, 'offline')
            return APIResponse.success()
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    
    @enginefacade.transactional
    def register(self, session, user_name:str, password:str, is_admin:bool):
        """
        create user
        """
        try:
            user = db.get_user_by_name(session, user_name)
            if user is not None:
                return APIResponse.error(code=401, msg="user name has been used")
            en_password = encrypt_passwd(password)
            user = db.create_user(session, user_name, en_password, is_admin)
            uuid = user.uuid
            storage_api.create_pool(name = user_name, allocation = CONF['volume']['pool_default_allocation'], user_id = uuid)
            return APIResponse.success(data=uuid)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
    @enginefacade.transactional
    def unregister(self, session, user_name:str):
        """
        delete user
        """
        try:
            user = db.get_user_by_name(session, user_name)
            if user is None:
                return APIResponse.error(code=402, msg="user does not exit")
            db.delete_user_by_name(session, user_name)
            # TODO: delete all user resources?
            
            return APIResponse.success()
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    @enginefacade.transactional
    def change_password(self, session, user_name:str, old_password:str, new_password:str,):
        """
        change user password
        should provide old password
        """
        try:
            user: User = db.get_user_by_name(session, user_name)
            if user is None:
                return APIResponse.error(code=402, msg="user does not exit")
            
            if old_password == new_password:
                return APIResponse.error(code=402, msg="new password is the same as the old one")
            
            en_old_password = encrypt_passwd(old_password)
            if user.password != en_old_password:
                return APIResponse.error(code=403, msg="wrong old password")
            
            en_new_password = encrypt_passwd(new_password)
            db.update_user_password(session, user.uuid, en_new_password)
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    @enginefacade.transactional
    def get_user_list(self, session):
        try:
            users = db.get_user_list(session)
            res = [user.to_dict() for user in users]
            return APIResponse.success(res)
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    @enginefacade.transactional
    def get_user_uuid_by_name(self, session, user_name):
        try:
            user: User = db.get_user_by_name(session, user_name)
            if user is not None:
                return APIResponse.success(user.uuid)
            return APIResponse.error(code=401, msg="user does not exist")
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
        
        
    @enginefacade.transactional
    def get_current_user_uuid(self, session):
        user_name = g.get("user")
        user: User = db.get_user_by_name(session, user_name)
        if user:
            uuid = user.uuid
        else:
            uuid = None
        return APIResponse.success(uuid)
    
    
    @enginefacade.transactional
    def is_current_user_admin(self, session):
        user_name = g.get("user")
        user: User = db.get_user_by_name(session, user_name)
        if user and user.is_admin:
            return APIResponse.success(True)
        return APIResponse.success(False)


####################
# Helper Functions #
####################
def encrypt_passwd(password:str):
    return hashlib.sha256(password.encode()).hexdigest()
        
    
    