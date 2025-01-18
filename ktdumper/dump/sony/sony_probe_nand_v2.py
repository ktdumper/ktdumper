from dump.sony.sony_protocol_v2 import SonyProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.common.common_probe_nand import CommonProbeNand


class SonyProbeNand_v2(CommonProbeNand, RwAccess_v2, SonyProtocol_v2):
    pass
