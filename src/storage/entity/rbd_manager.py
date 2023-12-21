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

    def write_full_rbd(self, rbd_name: str, data: bytes):
        '''
            Write an entire object synchronously.
            
            The object is filled with the provided data. If the object exists,
            it is atomically truncated and then written.
        
            rbd_name: rbd name
            data: data to write
        '''
        try:
            return self.ioctx.write_full(rbd_name, data)
        except Exception as err:
            return str(err)

    def read_rbd(self, rbd_name: str, length=8192, offset=0):
        '''
            Read data from an object synchronously

            :param key: name of the object
            :param length: the number of bytes to read (default=8192)
            :param offset: byte offset in the object to begin reading at
        '''
        try:
            return self.ioctx.read(rbd_name, length, offset)
        except Exception as err:
            return str(err)

    def remove_rbd(self, rbd_name: str):
        '''delete rbd'''
        rbd_inst = rbd.RBD()
        try:
            return rbd_inst.remove(self.ioctx, rbd_name)
        except Exception as err:
            return str(err)

    def append_rbd(self, rbd_name: str, data: bytes):
        '''append data to a rbd'''
        try:
            return self.ioctx.aio_append(rbd_name, data)
        except Exception as err:
            return str(err)

    def resize_rbd(self, rbd_name: str, size):
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
        
    def delete_test(self, rbd_name: str):
        try:
            return self.ioctx.remove_object(rbd_name)
        except Exception as err:
            return str(err)
