from apscheduler.schedulers.background import BackgroundScheduler
from src.utils.singleton import singleton
from src.common.redis import RedisClient
from src.utils.config import CONF
from src.storage.storage_api import get_cluster_info
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
        
"""
A universal monitor, monitors not only domains,
but also slave machines and containers
"""
@singleton
class DomainMonitor:
    def __init__(self):
        self.scheduler = IntervalScheduler()
        self.redis = RedisClient()
        
        self.scheduler.add_interval_job(self.batch_store_domain_status)
        self.scheduler.add_interval_job(self.batch_store_slave_status)
        # comment this line if bug
        self.scheduler.add_interval_job(self.batch_store_container_status)
        
    def start_monitoring(self):
        self.scheduler.start_scheduler()
        
    def stop_monitoring(self):
        self.scheduler.stop_scheduler()
    
    def store_domain_status(self, domain_uuid: str, status_info):
        self.redis.add_value_to_list(domain_uuid, status_info)
        
    def store_container_status(self, container_uuid: str, status_info):
        self.redis.add_value_to_list(container_uuid, status_info)
        
        
    def get_stored_domain_status(self, domain_uuid:str):
        """
        get domain status stored in redis
        """
        return self.redis.get_list(domain_uuid)
    
    
    def get_stored_container_status(self, container_uuid:str):
        """
        get container status stored in redis
        """
        return self.redis.get_list(container_uuid)
    
    
    def get_stored_slave_status(self, slave_name:str):
        """
        get slave status stored in redis
        """
        return self.redis.get_list(slave_name)
    
    
    def get_all_stored_slave_status(self) -> dict:
        """
        get all slave status stored in redis
        """
        slaves = CONF['slaves']
        res = {}
        res["cluster_usage_info"] = self.redis.get_list("cluster_usage_info")
        for key, value in slaves.items():
            slave_name = key
            status_list = self.get_stored_slave_status(slave_name)
            res[slave_name] = status_list
        return res
    
    
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
        
        
    def batch_store_container_status(self):
        """
        store monitored data to redis,
        this function should be called every one minute    
        """
        from src.docker.api import DockerAPI
        docker_api = DockerAPI()
        uuid_2_data = {}
        data_list = docker_api.monitor_all().get_data()
        for data in data_list:
            if data is not None:
                uuid = data["uuid"]
                data_str = json.dumps(data)
                uuid_2_data[uuid] = data_str
    
        self.redis.add_values_to_list_transaction(uuid_2_data)
       
        
    def batch_store_slave_status(self):
        """
        store monitored slave data to redis,
        this function should be called every one minute    
        """
        from src.guest.api import SlaveAPI
        slaveapi = SlaveAPI()
        data_dict:dict = slaveapi.get_all_slave_status().get_data()
        cluster_usage_info = get_cluster_info().get_data()
        name_2_data = {}
        for key in data_dict.keys():
            value = data_dict.get(key)
            value_str = json.dumps(value)
            name_2_data[key] = value_str
        self.redis.add_values_to_list_transaction(name_2_data)
        self.redis.add_value_to_list("cluster_usage_info", json.dumps(cluster_usage_info))
