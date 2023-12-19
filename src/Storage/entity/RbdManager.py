import rbd
import rados


class RbdManager(object):
    def __init__(self, ioctx: rados.Ioctx):
        """
        :param ioctx: connect pool
        """
        if not ioctx:
            return "ioctx is none."
        self.ioctx = ioctx

    def get_rbd_inst(self):
        '''get RBD object'''
        try:
            return rbd.RBD()
        except Exception as err:
            return "get rbd object failed."+str(err)
        
    def get_image_inst(self, rbd_name):
        '''get Image object'''
        try:
            return rbd.Image(self.ioctx, rbd_name)
        except Exception as err:
            return "get image object failed."+str(err)

    def rbd_write(self, rbd_name: str, data: bytes):
        '''write data'''
        try:
            return self.ioctx.write_full(rbd_name, data)
        except Exception as err:
            return str(err)

    def rbd_read(self, rbd_name: str):
        '''read data'''
        try:
            return self.ioctx.read(rbd_name)
        except Exception as err:
            return str(err)

    def rbd_remove(self, rbd_name: str):
        '''delete data'''
        rbd_inst = rbd.RBD()
        try:
            return rbd_inst.remove(self.ioctx, rbd_name)
        except Exception as err:
            return str(err)

    def rbd_append(self, rbd_name: str, data: bytes):
        '''append data'''
        try:
            return self.ioctx.aio_append(rbd_name, data)
        except Exception as err:
            return str(err)

    def rbd_resize(self, rbd_name: str, size):
        '''resize rbd'''
        try:
            return self.ioctx.trunc(rbd_name, size)
        except Exception as err:
            return str(err)

    def xattr_write(self, rbd_name: str, xattr_name: str, data: bytes):
        '''write metadata into RBD with <key, value>,
        such as <author_name, Tom>'''
        try:
            return self.ioctx.set_xattr(rbd_name, xattr_name, data)
        except Exception as err:
            return str(err)

    def xattr_get(self, rbd_name: str, xattr_name: str):
        '''read metadata of RBD'''
        try:
            return self.ioctx.get_xattr(rbd_name, xattr_name)
        except Exception as err:
            return str(err)

    def list_rbd(self):
        '''list RBD objects'''
        rbd_inst = rbd.RBD()
        object_iterator = rbd_inst.list(self.ioctx)
        return object_iterator

    def create_rbd(self, ioctx: rados.Ioctx, volume_name: str, size: int):
        '''create RBD'''
        rbd_inst = rbd.RBD()
        try:
            return rbd_inst.create(ioctx, volume_name, size)
        except Exception as err:
            return str(err)
