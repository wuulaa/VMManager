from src.utils.sqlalchemy import enginefacade
from src.user.db.models import User
from src.utils.sqlalchemy.api import *

@enginefacade.auto_session
def create_user(session,
                name: str,
                password: str,
                is_admin: bool
                ):
    user = User(name, password, is_admin)
    insert(session, user)
    return user
    
@enginefacade.auto_session
def delete_user_by_uuid(session, uuid):
    user = select_by_uuid(session, User, uuid)
    delete(session, user)
    
@enginefacade.auto_session
def delete_user_by_name(session, name):
    user = select_by_name(session, User, name)
    delete(session, user)
    
@enginefacade.auto_session
def get_user_by_uuid(session, uuid):
    user = select_by_uuid(session, User, uuid)
    return user

@enginefacade.auto_session
def get_user_uuid_by_name(session, uuid):
    user:User = select_by_uuid(session, User, uuid)
    if user:
        return user.uuid
    return None
    
@enginefacade.auto_session
def get_user_by_name(session, name):
    user = select_by_name(session, User, name)
    return user

@enginefacade.auto_session
def update_user_state(session, uuid, state: str):
    condition_update(session, User, uuid, {"state": state})
    return select_by_uuid(session, User, uuid)

@enginefacade.auto_session
def update_user_token(session, uuid, token: str):
    condition_update(session, User, uuid, {"token": token})
    return select_by_uuid(session, User, uuid)

@enginefacade.auto_session
def update_user_password(session, uuid, password: str):
    condition_update(session, User, uuid, {"password": password})
    return select_by_uuid(session, User, uuid)

@enginefacade.auto_session
def get_user_list(session):
    return condition_select(session, User)

