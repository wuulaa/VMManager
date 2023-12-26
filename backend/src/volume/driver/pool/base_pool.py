import abc


class PoolDriver(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create(name):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(name):
        raise NotImplementedError()

    @abc.abstractmethod
    def resize(name, size):
        raise NotImplementedError()

    @abc.abstractmethod
    def query_all():
        raise NotImplementedError()

    @abc.abstractclassmethod
    def initialize_connection(cls):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def terminate_connection(cls) -> bool:
        raise NotImplementedError()
