import src.storage.storage_api as storage_api
from src.storage.entity.rbd_manager import RbdManager
from src.utils.response import APIResponse

cluster = storage_api.cluster
pool = storage_api.pool

class SnapShot():
    def __init__(self, pool_name: str, rbd_name: str) -> None:
        if not pool_name:
            raise Exception("pool_name is none")
        if not rbd_name:
            raise Exception("rbd name is none")
        
        # get pool connection
        self.ioctx = pool.get_ioctx_by_name(pool_name)
        self.rbd_name = rbd_name

    def get_image(self):
        rbd_manager = RbdManager(self.ioctx)
        image = rbd_manager.get_image_inst(self.rbd_name)
        return image
    
    def get_rbd(self):
        return RbdManager(self.ioctx).get_rbd_inst()
    
    def get_snap_info(self, snap_name: str):
        '''
            snap = dict{
            id:
            size:
            name:
            }
        '''
        image =None
        try:
            image = self.get_image()
            snapIterator = image.list_snaps()
            snapGenerator = snapIterator.__iter__()
            while True:
                try:
                    snap = next(snapGenerator)
                    if(snap.get("name")==snap_name):
                        return APIResponse.success(snap)
                except StopIteration:
                    break
            return APIResponse.error(code=400, msg="snapshot " + snap_name + "isn't exsit.")
        except Exception as err:
            return APIResponse.error(code=400, msg=str(err))
    
    def query_snaps(self):
        image =None
        try:
            image = self.get_image()
            snapIterator = image.list_snaps()
            snapGenerator = snapIterator.__iter__()
            snaps = []
            while True:
                try:
                    snaps.append(next(snapGenerator).get("name"))
                except StopIteration:
                    break
                except Exception as err:
                    return APIResponse.error(code=400, msg=str(err))
            return APIResponse.success(data=snaps)
        except Exception as err:
            return APIResponse.error(code=400, msg=str(err))
        finally:
            image.close()

    # def rename_snap(self, old_name: str, new_name: str):
    #     image =None
    #     try:
    #         image = self.get_image()
    #         snapIterator = image.list_snaps()
    #         snapGenerator = snapIterator.__iter__()
    #         while True:
    #             try:
    #                 snap = next(snapGenerator)
    #                 if(snap.get("name")==old_name):
    #                     snap['name'] = new_name
    #                     return APIResponse.success(snap)
    #             except StopIteration:
    #                 break
    #         return APIResponse.error(code=400, msg="snapshot " + old_name + "isn't exsit.")
    #     except Exception as err:
    #         return APIResponse.error(code=400, msg=str(err))
    #     finally:
    #         image.close()
    
    def is_snap_exits(self, snap_name):
        try:
            snaps = self.query_snaps()
            if snaps is None:
                return False
            if snap_name in snaps:
                return True
            return False
        except Exception as err:
            raise Exception(str(err))
    
    def create_snap(self, snap_name):
        image =None
        try:
            if self.is_snap_exits(snap_name):
                return APIResponse.error(code=400, msg = "snapshot " + snap_name + " already exists.")
            image = self.get_image()
            image.create_snap(snap_name)
            return APIResponse.success()
        except Exception as err:
            return APIResponse.error(code=400, msg=str(err))
        finally:
            image.close()
    
    def delete_snap(self, snap_name):
        image = None
        try:
            image = self.get_image()
            image.remove_snap(snap_name)
            return APIResponse.success()
        except Exception as err:
            return APIResponse.error(code=400, msg=str(err))
        finally:
            image.close()

    def is_snap_protected(self, snap_name):
        image = None
        try:
            image = self.get_image()
            return image.is_protected_snap(snap_name)
        except Exception as err:
            raise Exception('check snap protected failed.')
        finally:
            image.close()

    def protect_snap(self, snap_name):
        image = None
        try:
            if not self.is_snap_protected(snap_name):
                image = self.get_image()
                image.protect_snap(snap_name)
        except Exception as err:
            raise Exception('protect snap failed.')
        finally:
            image.close()

    def unprotect_snap(self, snap_name):
        image = None
        try:
            if self.get_children_list(snap_name):
                raise Exception('cannot unprotect: snap has at least one children.')
            if self.is_snap_protected(snap_name):
                image = self.get_image()
                image.unprotect_snap(snap_name)
        except Exception as err:
            raise Exception('unprotect snap failed.')
        finally:
            image.close()

    def get_children_list(self, snap_name):
        image = None
        try:
            children = []
            image = self.get_image()
            image.set_snap(snap_name)
            list_children = image.list_children()
            for i in list_children:
                children.append({'pool_name': i[0].encode(),'image_name': i[1].encode()})
            return children
        except Exception as err:
            raise Exception('get children failed.' + str(err))
        finally:
            image.close()

    def batch_create_snaps(self, snap_name_list: list):
        for name in snap_name_list:
            self.create_snap(name)

    def clone(self, snap_name, dest_pool_name, dest_rbd_name):
        try:
            if not self.is_snap_exits(snap_name):
                return APIResponse.error(code=400, msg='snap not exists.')
            if not self.is_snap_protected(snap_name):
                self.protect_snap(snap_name)
            rbd_inst = self.get_rbd()
            c_ioctx = pool.get_ioctx_by_name(dest_pool_name)
            rbd_inst.clone(self.ioctx, self.rbd_name, snap_name, c_ioctx, dest_rbd_name)
            return APIResponse.success()
        except Exception as err:
            return APIResponse.error(code=400, msg=str(err))
        
    def rollback_to_snap(self, snap_name: str):
        try:
            if not self.is_snap_exits(snap_name):
                return APIResponse.error(code=400, msg='snap not exists.')
            image_inst = self.get_image()
            image_inst.rollback_to_snap(snap_name)
            return APIResponse.success()
        except Exception as err:
            return APIResponse.error(code=400, msg=str(err))



