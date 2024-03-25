from apscheduler.schedulers.background import BackgroundScheduler
from src.utils.singleton import singleton
from src.common.redis import RedisClient
from src.utils.config import CONF
import json

scheduler_interval = CONF["redis"].getint("scheduler_interval")

@singleton
class IntervalScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.ids = []

    def add_interval_job(self, func, interval=scheduler_interval):
        job = self.scheduler.add_job(func=func, trigger='interval', seconds=interval)
        self.ids.append(job.id)
    
    def remove_job(self, id):
        self.scheduler.remove_job(id)
        
    def start_scheduler(self):
        self.scheduler.start()
        
    def stop_scheduler(self):
        self.scheduler.shutdown()
        
        
@singleton
class DomainMonitor:
    def __init__(self):
        self.scheduler = IntervalScheduler()
        self.redis = RedisClient()
        
        self.scheduler.add_interval_job(self.batch_store_domain_status)
        
    def start_monitoring(self):
        self.scheduler.start_scheduler()
        
    def stop_monitoring(self):
        self.scheduler.stop_scheduler()
    
    def store_domain_status(self, domain_uuid: str, status_info):
        self.redis.add_value_to_list(domain_uuid, status_info)
        
        
    def get_stored_domain_status(self, domain_uuid:str):
        """
        get all domain status stored in redis
        """
        return self.redis.get_list(domain_uuid)
    
    
    def batch_store_domain_status(self):
        """
        store monitored data to redis,
        this function should be called every one minute    
        """
        from src.guest.api import GuestAPI
        guest_api = GuestAPI()
        uuid_2_data = {}
        data_list = guest_api.monitor_all().get_data()
        for data in data_list:
            if data is not None:
                uuid = data["uuid"]
                data_str = json.dumps(data)
                uuid_2_data[uuid] = data_str
    
        self.redis.add_values_to_list_transaction(uuid_2_data)
        
        
    
