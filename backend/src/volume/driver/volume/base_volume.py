import abc


class VolumeDriver(object, metaclass=abc.ABCMeta):

    @abc.abstractstaticmethod
    def clone(src_volume_name: str,
              snap_name: str,
              dest_name: str):
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def create(volume_name: str, allocation: int):
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def delete(volume_name):
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def get_volume_info(volume_name):
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def rename(volume_name, new_name):
        raise NotImplementedError()


class SnapshotDriver(object, metaclass=abc.ABCMeta):

    @abc.abstractclassmethod
    def create(volume_name: str, snap_name: str):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def delete(volume_name: str, snap_name: str):
        raise NotImplementedError()
