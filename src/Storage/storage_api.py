from src.Storage.entity.Cluster import Cluster
from src.Storage.entity.Pool import Pool
from src.Storage.entity.RbdManager import RbdManager
from src.Utils.response import APIResponse
from src.Storage.entity.path import CEPH_PATH


cluster = Cluster(CEPH_PATH)
pool = Pool(cluster)

def query_rbd(pool_name: str):
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
    response = query_rbd(pool_name)
    list_rbd = response.result
    for name in list_rbd:
        if(name == rbd_name):
            return True
    return False
    

def create_pool(pool_name: str):
    '''create pool'''
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
    '''delete pool'''
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


def write_rbd(pool_name: str, rbd_name: str, data: bytes):
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
        rbd.rbd_write(rbd_name, data)
        response.is_success = True
        response.description = "write successfully."
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    finally:
        ioctx.close()
    return response


def read_rbd(pool_name: str, rbd_name: str):
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
        response.result = rbd.rbd_read(rbd_name)
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
        rbd.rbd_remove(rbd_name)
        response.description = "delete successfully."
        response.is_success = True
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    finally:
        ioctx.close()
    return response


def append_rbd(pool_name: str, rbd_name: str, data: bytes):
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
        err = rbd.rbd_append(rbd_name, data)
        response.is_success = True
        response.description = "append successfully."+ str(err)
    except Exception as err:
        response.is_success = False
        response.description = str(err)
    finally:
        ioctx.close()
    return response


def create_rbd(pool_name: str, rbd_name: str, size: int):
    '''create RBD'''
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
