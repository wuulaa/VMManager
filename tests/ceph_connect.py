import rados
from src.storage.storage_api import *
import rbd
from src.utils.response import APIResponse
from src.image.ISO.ISOApi import ISOApi

# cluster = rados.Rados(conffile='/etc/ceph/ceph.conf')

# cluster.connect()

# response = create_pool("images")
# print(response.json())

# response = query_pool() 
# print(response.get_data())

# response = read_rbd("images", "rbd3")
# print(response.data)

# response = append_rbd("test", "image1", b"aaaaa")
# print(response.json())

# response = delete_rbd("images", "image2")
# print(response.get_msg())

# response = create_rbd("images", "image1", 10)
# print(response.get_msg())

print(query_rbd("images").data)

