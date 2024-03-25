import redis
from src.utils.singleton import singleton
from src.utils.config import CONF

redis_port = CONF["redis"]["redis_port"]
db = CONF["redis"].getint("db")
max_store_length = CONF["redis"].getint("max_store_length")

@singleton
class RedisClient:
    def __init__(self, port=redis_port, db=db) -> None:
        self.redis_client = redis.StrictRedis(host='localhost', port=port, db=db, decode_responses=True)
        self.max_length = max_store_length
    

    def add_value_to_list(self, key, value):
        # 如果列表长度超过了最大长度，先修剪列表
        if self.redis_client.llen(key) >= self.max_length:
            self.redis_client.ltrim(key, -self.max_length, -1)
        # 添加新值到列表的末尾
        self.redis_client.rpush(key, value)
        
        
    def add_values_to_list_transaction(self, data_dict:dict):
        # 开启一个事务
        transaction = self.redis_client.pipeline()
        keys = data_dict.keys()
        for key in keys:
            value = data_dict.get(key)
            transaction.rpush(key, value)
        transaction.execute()

        # 获取列表的长度，并进行修剪
        for key in data_dict.keys():
            # 获取列表的长度
            length = self.redis_client.llen(key)
            # 如果列表长度超过了最大长度，修剪列表
            if length >= self.max_length:
                self.redis_client.ltrim(key, -self.max_length, -1)


    def get_list(self, key):
        if self.redis_client.exists(key):
            # 获取列表所有元素
            return self.redis_client.lrange(key, 0, -1)
        return []

