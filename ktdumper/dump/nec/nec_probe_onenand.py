from dump.common.common_probe_onenand import CommonProbeOnenand
from dump.nec.nec_protocol import NecProtocol
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess


class NecProbeOnenand(CommonProbeOnenand, NecPiplRwAccess, NecProtocol):
    pass
