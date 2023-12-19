import rados


class Pool(object):

    def __init__(self, cluster):
        """
        :param cluster: ceph connect
        """
        if not cluster:
            return "cluster is none."
        self.cluster = cluster.cluster

    def get_ioctx_by_name(self, pool_name: str):
        '''connect pool by pool_name'''
        try:
            return self.cluster.open_ioctx(pool_name)
        except Exception as err:
            return str(err)

    def get_ioctx_by_id(self, pool_id: str):
        '''connect pool by pool_id'''
        try:
            return self.cluster.open_ioctx2(pool_id)
        except Exception as err:
            return str(err)

    def close_ioctx(ioctx: rados.Ioctx):
        '''close pool connect'''
        try:
            ioctx.close()
        except Exception as err:
            return str(err)

    def list_pools(self):
        '''list available pools'''
        try:
            pools = self.cluster.list_pools()
            return pools
        except Exception as err:
            return str(err)

    def exists_pool(self, pool_name: str):
        '''check pool'''
        try:
            if(self.cluster.pool_exists(pool_name)):
                return True
            else:
                return False
        except Exception as err:
            return str(err)

    def create_pool(self, pool_name: str):
        '''create pool'''
        try:
            if self.exists_pool(pool_name):
                raise Exception(f'pool {pool_name} is exist')
            self.cluster.create_pool(pool_name)
            return "success"
        except Exception as err:
            return str(err)

    def delete_pool(self, pool_name: str):
        '''delete pool'''
        try:
            self.cluster.delete_pool(pool_name)
        except Exception as err:
            return str(err)
