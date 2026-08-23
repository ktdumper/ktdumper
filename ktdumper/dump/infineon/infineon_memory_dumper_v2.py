from dump.common.common_memory_dumper import CommonMemoryDumper
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.infineon.infineon_exploit_v2 import InfineonExploit_v2


class InfineonMemoryDumper_v2(CommonMemoryDumper, RwAccess_v2, InfineonExploit_v2):
    pass
