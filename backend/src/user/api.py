from src.user.service import UserService
from src.utils.response import APIResponse

user_service = UserService()


class UserAPI:

    def login(self, username, passwd) -> APIResponse:
        return user_service.login(username=username, passwd=passwd)
    
    def logout(self, username) -> APIResponse:
        return user_service.logout(username=username)
        
    def register(self, user_name:str, password:str, is_admin:bool) -> APIResponse:
        return user_service.register(user_name=user_name, password=password, is_admin=is_admin)
    
    def unregister(self, user_name:str) -> APIResponse:
        return user_service.unregister(user_name=user_name)
    
    def change_password(self, user_name:str, old_password:str, new_password:str) -> APIResponse:
        return user_service.change_password(user_name=user_name,
                                            old_password=old_password,
                                            new_password=new_password)
   
    def get_user_list(self) -> APIResponse:
        return user_service.get_user_list()
    
    def get_user_uuid_by_name(self, user_name) -> APIResponse:
        return user_service.get_user_uuid_by_name(user_name=user_name)
    
    def get_user_name_by_uuid(self, user_uuid) -> APIResponse:
        return user_service.get_user_name_by_uuid(user_uuid=user_uuid)
    
    def get_current_user_uuid(self) -> APIResponse:
        return user_service.get_current_user_uuid()
    
    def is_current_user_admin(self) -> APIResponse:
        return user_service.is_current_user_admin()
    
    def get_current_user_name(self) -> APIResponse:
        return user_service.get_current_user_name()
    
    def get_user_last_login(self, user_name) -> APIResponse:
        return user_service.get_user_last_login(user_name=user_name)
    
