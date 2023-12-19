import abc


class VolumeDriver(object, metaclass=abc.ABCMeta):

    @abc.abstractstaticmethod
    def clone(src_pool, src_volume, dest_pool, dest_name):
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def close_volume(volume_name):
        raise NotImplementedError()

    @abc.abstractstaticmethod
    def create(volume_name, allocation):
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
