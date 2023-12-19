import rados
from src.storage.storage_api import *
import rbd
from src.utils.response import APIResponse
from src.image.image_api import *

# cluster = rados.Rados(conffile='/etc/ceph/ceph.conf')

# cluster.connect()

# response = create_pool("images")
# print(response.json())

response = query_pool() 
print(response.json())

# response = write_rbd("test", "image1", b"hello world!")
# print(response.json())

# response = read_rbd("images", "test_image")
# print(response.result)

# response = append_rbd("test", "image1", b"aaaaa")
# print(response.json())

# response = read_rbd("test", "image1")
# print(response.result)

# response = delete_rbd("libvirt-pool", "concurrency2")
# print(response.json())

# response = create_rbd("images", "volume1", 10*1024*1024*1024)
# print(response.json())

# print(query_rbd("libvirt-pool").result)

# response = upload_image("image1", "/home/kvm/images/ubuntu-22.04.3-live-server-arm64.iso")
# print(response.json())

# response = query_images()
# print(response.result)

# response = delete_rbd("images", "test_image")
# print(response.json())

# read_image("test_image2")

# cluster.shutdown()

