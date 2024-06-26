from src.storage.entity.rbd_manager import RbdManager
from src.utils.response import APIResponse
from src.image.snapshot.snapshot import SnapShot
from src.storage.conf import pool
from src.storage.conf import cluster
import time

error_info = {
    1:"pool isn't exist.",
    2:"rbd isn't exist.",
    3:"rbd already exist.",
    400:"unknown exception"
}

def query_rbds(pool_name: str) -> APIResponse:
    '''
        query rbds in chosen pool
        pool_name: chosen pool name
    '''

    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1,msg=error_info[1])
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        objects = rbd.list_rbd()
        return APIResponse.success(objects)
    except Exception as err:
        return APIResponse.error(code=400,msg=str(err))
    finally:
        if ioctx is not None:
            ioctx.close()


def exist_rbd(pool_name:str ,rbd_name:str) -> APIResponse:
    '''
        check rbd named rbd_name exist or not
        pool_name: pool name
        rbd_name: rbd name
    '''
    response = query_rbds(pool_name)
    list_rbd = response.data
    for name in list_rbd:
        if(name == rbd_name):
            return True
    return False

def create_pool(pool_name: str) -> APIResponse:
    ''' 
        create pool named pool_name
        pool_name: pool name
    '''
    description = pool.create_pool(pool_name)
    if(description == "success"):
        return APIResponse.success()
    else:
        return APIResponse.error(code=400, msg=description)

def query_pools() -> APIResponse:
    '''query pool'''

    try:
        result = pool.list_pools()
        return APIResponse.success(data=result)
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))

def delete_pool(pool_name: str) -> APIResponse:
    '''
        delete pool named pool_name
        pool_name: pool name
    '''

    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1, msg=error_info[1])
    description = pool.delete_pool(pool_name)
    if(description == "success"):
        return APIResponse.success()
    else:
        return APIResponse.error(code=400, msg=description)

def write_full_rbd(pool_name: str, rbd_name: str, object_name: str, data: bytes) -> APIResponse:
    '''
        write data into rbd
        pool_name: pool name
        rbd_name: rbd name
        data: the data will be writed
        Be carefully!!! This writed data will cover original data in the rbd.
        If you just want to write data without covering data, please call function append_rbd()
    '''

    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1, msg=error_info[1])
    if(exist_rbd(pool_name, rbd_name) == False):
        return APIResponse.error(code=2, msg=error_info[2])
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        rbd.write_full_rbd(object_name, data)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally:
        if ioctx is not None:
            ioctx.close()


def append_rbd(pool_name: str, rbd_name: str, data: bytes) -> APIResponse:
    '''
        append data to rbd
        pool_name: pool name 
        rbd_name: rbd name
        data: the data will be appened
    '''

    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1, msg=error_info[1])
    if(exist_rbd(pool_name, rbd_name) == False):
        return APIResponse.error(code=2, msg=error_info[2])
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        err = rbd.append_rbd(rbd_name, data)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally:
        if ioctx is not None:
            ioctx.close()


def read_rbd(pool_name: str, rbd_name: str, offset=0, length=8192) -> APIResponse:
    '''
        read rbd
        pool_name: pool name
        rbd_name: rbd name
    '''

    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1, msg=error_info[1])
    if(exist_rbd(pool_name, rbd_name) == False):
        return APIResponse.error(code=2, msg=error_info[2])
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        result = rbd.read_rbd(rbd_name, offset, length)
        return APIResponse.success(result)
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally: 
        if ioctx is not None:
            ioctx.close()


def delete_rbd(pool_name: str, rbd_name: str) -> APIResponse:
    '''
        delete rbd
        pool_name: pool name
        rbd_name: rbd name
        This method will delete rbd permanently.
    '''

    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1, msg=error_info[1])
    if(exist_rbd(pool_name, rbd_name) == False):
        return APIResponse.error(code=2, msg=error_info[2])
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        rbd.remove_rbd(rbd_name)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally:
        if ioctx is not None:
            ioctx.close()


def create_rbd(pool_name: str, rbd_name: str, size: int) -> APIResponse:
    '''
        create rbd
        pool_name: pool name
        rbd_name: rbd name
        size: rbd size. For example size=1024, rbd = 1024(Bytes).
    '''
    if(pool.exists_pool(pool_name) == False):
        return APIResponse.error(code=1, msg=error_info[1])
    if(exist_rbd(pool_name, rbd_name) == True):
        return APIResponse.error(code=3, msg=error_info[3])
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(pool)
        description = rbd.create_rbd(ioctx, rbd_name, size)
        if(description == "success"):
            return APIResponse.success()
        else:
            return APIResponse.error(code=400, msg=description)
    finally:
        if ioctx is not None:
            ioctx.close()


def clone(pool_name: str, rbd_name: str, snap_name: str, dest_pool_name: str, dest_rbd_name: str) -> APIResponse:
    snap = SnapShot(pool_name, rbd_name)
    try:
        if not snap.is_snap_exits(snap_name):
            return APIResponse.error(code=400, msg='snap not exists.')
        if not snap.is_snap_protected(snap_name):
            snap.protect_snap(snap_name)
        rbd_inst = snap.get_rbd()
        c_ioctx = pool.get_ioctx_by_name(dest_pool_name)
        rbd_inst.clone(snap.ioctx, snap.rbd_name, snap_name, c_ioctx, dest_rbd_name)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))


def create_snap(pool_name: str, rbd_name: str, snap_name: str) -> APIResponse:
    snap = SnapShot(pool_name, rbd_name)
    image = snap.get_image()
    try:
        if snap.is_snap_exits(snap_name):
            return APIResponse.error(code=400, msg = "snapshot " + snap_name + " already exists.")
        image.create_snap(snap_name)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally:
        if image is not None:  
            image.close()


def delete_snap(pool_name: str, rbd_name: str, snap_name: str) -> APIResponse:
    snap = SnapShot(pool_name, rbd_name)
    image = snap.get_image()
    try:
        snap.unprotect_snap(snap_name)
        image.remove_snap(snap_name)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally:
        if image is not None:  
            image.close()


def query_snaps(pool_name: str, rbd_name: str) -> APIResponse:
    snap = SnapShot(pool_name, rbd_name)
    return APIResponse.success(data=snap.query_snaps())


def rollback_to_snap(pool_name: str, rbd_name: str, snap_name: str) -> APIResponse:
    snap = SnapShot(pool_name, rbd_name)
    try:
        if not snap.is_snap_exits(snap_name):
            return APIResponse.error(code=400, msg='snap not exists.')
        image_inst = snap.get_image()
        image_inst.rollback_to_snap(snap_name)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))


def rename_rbd(pool_name: str, rbd_name: str, new_name: str) -> APIResponse:
    ioctx = pool.get_ioctx_by_name(pool_name)
    rbd_instance = RbdManager(ioctx)
    try:
        rbd_instance.rename_rbd(ioctx, rbd_name, new_name)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.err(code=400, msg=str(err))
    finally:
        if ioctx is not None:
            ioctx.close()
    

def resize_rbd(pool_name: str, rbd_name: str, size: str) -> APIResponse:
    ioctx = pool.get_ioctx_by_name(pool_name)
    rbd_instance = RbdManager(ioctx)
    try:
        rbd_instance.resize_rbd(ioctx, rbd_name, size)
        return APIResponse.success()
    except Exception as err:
        return APIResponse.err(code=400, msg=str(err))
    finally:
        if ioctx is not None:
            ioctx.close()
    

def info_snap(pool_name: str, rbd_name: str, snap_name: str) -> APIResponse:
    snap = SnapShot(pool_name, rbd_name)
    '''
        snap = dict{
        id:
        size:
        name:
        }
    '''
    image = snap.get_image()
    try:
        snapIterator = image.list_snaps()
        snapGenerator = snapIterator.__iter__()
        while True:
            try:
                snap = next(snapGenerator)
                if(snap.get("name")==snap_name):
                    return APIResponse.success(data=snap)
            except StopIteration:
                break
        return APIResponse.error(code=400, msg="snapshot " + snap_name + "isn't exsit.")
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    finally:
        if image is not None:
            image.close()

def get_cluster_info() -> APIResponse:
    '''read usage info about the cluster'''
    try:
        dict = cluster.get_cluster_info()
        dict["time"] = time.localtime()
        return APIResponse.success(dict)
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))
    
# snaps_list = query_snaps(pool_name="volume-pool", rbd_name="template1").get_data()
# for snap in snaps_list:
#     delete_snap(pool_name="volume-pool", rbd_name="template1", snap_name=snap)

# print(get_cluster_info().to_json_str())