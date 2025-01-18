from dump.common.common_memory_dumper import CommonMemoryDumper
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.sony.sony_protocol_v2 import SonyProtocol_v2


class SonyMemoryDumper_v2(CommonMemoryDumper, RwAccess_v2, SonyProtocol_v2):
    pass
