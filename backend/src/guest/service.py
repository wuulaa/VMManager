from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.guest.db.models import Guest
import src.volume.db as db

@singleton
class GuestService():
    @enginefacade.transactional
    def create_guest():
        return
    
    @enginefacade.transactional
    def start_guest():
        return
    
    @enginefacade.transactional
    def shutdown_guest():
        return
    
    @enginefacade.transactional
    def destroy_guest():
        return
    
    @enginefacade.transactional
    def pause_guest():
        return
    
    @enginefacade.transactional
    def delete_guest():
        return
    
    @enginefacade.transactional
    def get_uuid_by_name(vm_name: str):
        return db.select_by_name(Guest, vm_name).uuid
    
