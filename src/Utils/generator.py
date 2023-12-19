import uuid

from typing import Optional


class UUIDGenerator(object):
    @staticmethod
    def get_uuid(exist_uuid: Optional[list] = []) -> str:
        ''' generate a non-conflicting UUID
        为了保证 UUID 的唯一性，新生成的 UUID 不能与已存在的
        重复，因此需要将过往的 UUID 作为参数传入进行对比。

        exist_uuid: 过往生成的 UUID
        @return 新生成的 UUID
        '''
        for ignore in range(256):
            gen_uuid = str(uuid.uuid4())
            if (gen_uuid in exist_uuid):
                continue
            return gen_uuid
        raise Exception("Failed to generate non-conflicting UUID")
