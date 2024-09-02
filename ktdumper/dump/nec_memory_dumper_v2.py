from dump.nec_protocol_v2 import NecProtocol_v2
from dump.nec_rw_access_v2 import NecRwAccess_v2
from dump.common_memory_dumper import CommonMemoryDumper


class NecMemoryDumper_v2(CommonMemoryDumper, NecRwAccess_v2, NecProtocol_v2):
    pass
