import src.storage.storage_api as storage_api
from src.storage.entity.rbd_manager import RbdManager

cluster = storage_api.cluster
pool = storage_api.pool

class ISOApi():

    #添加镜像
    def add_image(image_name: str, file_path: str):
        with open(file_path, 'rb') as f:
            data = f.read()
            storage_api.create_rbd("images", image_name, len(data)) 
            ioctx = pool.get_ioctx_by_name("images")
            rbd_manager = RbdManager(ioctx)
            image = rbd_manager.get_image_inst(image_name)
            image.write(data, 0)
        image.close()
        ioctx.close()

    def read_image(image_name: str):
        ioctx = pool.get_ioctx_by_name("images")
        rbd_manager = RbdManager(ioctx)
        image = rbd_manager.get_image_inst(image_name)
        image.read()
        image.close()
        ioctx.close()

    #获取镜像列表
    def query_images():
        return storage_api.query_rbds("images")

    #镜像详情
    def image_info(image_name: str):
        return storage_api.qu

    #删除镜像
    def delete_image(image_name: str):
        return storage_api.delete_rbd("images", image_name)


