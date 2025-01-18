from dump.sony.sony_protocol_v2 import SonyProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.common.common_nor_probe import CommonNorProbe


class SonyProbeNor_v2(CommonNorProbe, RwAccess_v2, SonyProtocol_v2):
    pass
