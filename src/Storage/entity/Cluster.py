import rados
import os


class Cluster(object):

    def __init__(self, conf):
        if not conf:
            return "conf is none."
        if not os.path.exists(conf):
            return "conf file not exits."
        self.conf = conf
        self.cluster = self.get_cluster()
        self.connect_cluster()

    def get_cluster(self):
        '''get Ceph cluster'''
        try:
            return rados.Rados(conffile=self.conf)
        except Exception as err:
            return str(err)

    def connect_cluster(self):
        '''connect Ceph cluster'''
        try:
            self.cluster.connect()
        except Exception as err:
            return str(err)

    def close_cluster(self):
        '''close connect'''
        try:
            self.cluster.shutdown()
        except Exception as err:
            return str(err)
