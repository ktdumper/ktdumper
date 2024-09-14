from dump.nec.nec_protocol_v2 import NecProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.common.common_memory_dumper import CommonMemoryDumper


class NecMemoryDumper_v2(CommonMemoryDumper, RwAccess_v2, NecProtocol_v2):
    pass
