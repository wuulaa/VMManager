from src.storage.entity.cluster_manager import Cluster
from src.storage.entity.pool_manager import Pool
from src.storage.entity.rbd_manager import RbdManager
from src.utils.response import APIResponse
from src.storage.entity.path import CEPH_PATH


cluster = Cluster(CEPH_PATH)
pool = Pool(cluster)

def query_rbd(pool_name: str):
    '''
        query rbds in chosen pool
        pool_name: chosen pool name
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        objects = rbd.list_rbd()
        response.result = objects
        response.is_success = True
        response.description = "query successfully."
    except Exception as err:
        response.result = None
        response.is_success = False
        response.description = "Fail to query. " + str(err)
    finally:
        ioctx.close()
    return response

def exist_rbd(pool_name:str ,rbd_name:str):
    '''
        check rbd named rbd_name exist or not
        pool_name: pool name
        rbd_name: rbd name
    '''
    response = query_rbd(pool_name)
    list_rbd = response.result
    for name in list_rbd:
        if(name == rbd_name):
            return True
    return False

def create_pool(pool_name: str):
    ''' 
        create pool named pool_name
        pool_name: pool name
    '''
    response = APIResponse()
    response.description = pool.create_pool(pool_name)
    if(response.description == "success"):
        response.is_success = True
    else:
        response.is_success = False
    return response

def query_pool():
    '''query pool'''
    response =APIResponse()
    try:
        response.result = pool.list_pools()
        response.is_success = True
    except Exception as err:
        response.description = str(err)
        response.is_success = False
    return response

def delete_pool(pool_name: str):
    '''
        delete pool named pool_name
        pool_name: pool name
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    try:
        pool.delete_pool(pool_name)
        response.is_success = True
        response.description = "delete "+pool_name+" successfully."
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    return response

def write_full_rbd(pool_name: str, rbd_name: str, object_name: str, data: bytes):
    '''
        write data into rbd
        pool_name: pool name
        rbd_name: rbd name
        data: the data will be writed
        Be carefully!!! This writed data will cover original data in the rbd.
        If you just want to write data without covering data, please call function append_rbd()
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    if(exist_rbd(pool_name, rbd_name) == False):
        response.is_success = False
        response.description = "Rbd " + rbd_name + " isn't exist. Please call function create_rbd(pool_name, rbd_name, size:int) to create rbd." 
        return response
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        rbd.write_full_rbd(object_name, data)
        response.is_success = True
        response.description = "write successfully."
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    finally:
        ioctx.close()
    return response

def append_rbd(pool_name: str, rbd_name: str, data: bytes):
    '''
        appen data to rbd
        pool_name: pool name 
        rbd_name: rbd name
        data: the data will be appened
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    if(exist_rbd(pool_name, rbd_name) == False):
        response.is_success = False
        response.description = "Rbd " + rbd_name + " isn't exist." 
        return response
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        err = rbd.append_rbd(rbd_name, data)
        response.is_success = True
        response.description = "append successfully."+ str(err)
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    finally:
        ioctx.close()
    return response

def read_rbd(pool_name: str, rbd_name: str):
    '''
        read rbd
        pool_name: pool name
        rbd_name: rbd name
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    if(exist_rbd(pool_name, rbd_name) == False):
        response.is_success = False
        response.description = "Rbd " + rbd_name + " isn't exist." 
        return response
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        response.result = rbd.read_rbd(rbd_name)
        response.description = "read "+rbd_name+" successfully."
        response.is_success = True
    except Exception as err:
        response.is_success = False
        response.description = str(err)
        response.result = None
    finally: 
        ioctx.close()
    return response

def delete_rbd(pool_name: str, rbd_name: str):
    '''
        delete rbd
        pool_name: pool name
        rbd_name: rbd name
        This method will delete rbd permanently.
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    if(exist_rbd(pool_name, rbd_name) == False):
        response.is_success = False
        response.description = "Rbd " + rbd_name + " isn't exist." 
        return response
    ioctx = pool.get_ioctx_by_name(pool_name)
    try:
        rbd = RbdManager(ioctx)
        rbd.remove_rbd(rbd_name)
        response.description = "delete successfully."
        response.is_success = True
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    finally:
        ioctx.close()
    return response

def create_rbd(pool_name: str, rbd_name: str, size: int):
    '''
        create rbd
        pool_name: pool name
        rbd_name: rbd name
        size: rbd size. For example size=1024, rbd = 1024(Bytes).
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    if(exist_rbd(pool_name, rbd_name) == True):
        response.is_success = False
        response.description = "Rbd " + rbd_name + " is exist." 
        return response
    try:
        ioctx = pool.get_ioctx_by_name(pool_name)
        try:
            rbd = RbdManager(pool)
            result = rbd.create_rbd(ioctx, rbd_name, size)
            if(result == None):
                response.is_success = True
                response.description = "create rbd successfully."
            else:
                response.description = "failt to create rbd " + str(result)
                response.is_success = False
        finally:
            ioctx.close()
    except Exception as err:
        response.description = "failt to create rbd " + str(err)
        response.is_success = False
    return response

def get_rbd_info(pool_name: str, rbd_name: str):
    '''
        get rbd detail info
        pool_name: pool name
        rbd_name: rbd name
    '''
    response = APIResponse()
    if(pool.exists_pool(pool_name) == False):
        response.is_success = False
        response.description = "Pool " + pool_name + " isn't exist." 
        return response
    if(exist_rbd(pool_name, rbd_name) == True):
        response.is_success = False
        response.description = "Rbd " + rbd_name + " is exist." 
        return response
    try:
        ioctx = pool.get_ioctx_by_name(pool_name)
        try:
            rbd = RbdManager(pool)
            
            result = rbd.create_rbd(ioctx, rbd_name, size)
            if(result == None):
                response.is_success = True
                response.description = "create rbd successfully."
            else:
                response.description = "failt to create rbd " + str(result)
                response.is_success = False
        finally:
            ioctx.close()
    except Exception as err:
        response.description = "failt to create rbd " + str(err)
        response.is_success = False
    return response
