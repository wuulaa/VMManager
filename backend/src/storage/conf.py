from src.storage.entity.cluster_manager import Cluster
from src.storage.entity.pool_manager import Pool
from src.storage.entity.path import CEPH_PATH

cluster = Cluster(CEPH_PATH)
pool = Pool(cluster)
