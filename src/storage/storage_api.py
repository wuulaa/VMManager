from src.storage.entity.cluster_manager import Cluster
from src.storage.entity.pool_manager import Pool
from src.storage.entity.rbd_manager import RbdManager
from src.utils.response import APIResponse
from src.storage.entity.path import CEPH_PATH

error_info = {
    1:"pool isn't exist.",
    2:"rbd isn't exist.",
    3:"rbd already exist.",
    400:"unknown exception"
}

cluster = Cluster(CEPH_PATH)
pool = Pool(cluster)

def query_rbds(pool_name: str):
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
        ioctx.close()


def exist_rbd(pool_name:str ,rbd_name:str):
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

def create_pool(pool_name: str):
    ''' 
        create pool named pool_name
        pool_name: pool name
    '''
    description = pool.create_pool(pool_name)
    if(description == "success"):
        return APIResponse.success()
    else:
        return APIResponse.error(code=400, msg=description)

def query_pools():
    '''query pool'''

    try:
        result = pool.list_pools()
        return APIResponse.success(data=result)
    except Exception as err:
        return APIResponse.error(code=400, msg=str(err))

def delete_pool(pool_name: str):
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

def write_full_rbd(pool_name: str, rbd_name: str, object_name: str, data: bytes):
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
        ioctx.close()


def append_rbd(pool_name: str, rbd_name: str, data: bytes):
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
        ioctx.close()


def read_rbd(pool_name: str, rbd_name: str, offset=0, length=8192):
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
        ioctx.close()


def delete_rbd(pool_name: str, rbd_name: str):
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
        ioctx.close()


def create_rbd(pool_name: str, rbd_name: str, size: int):
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
        ioctx.close()
