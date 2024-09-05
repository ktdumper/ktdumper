from dump.nec.nec_protocol_v2 import NecProtocol_v2
from dump.rw_access_v2 import RwAccess_v2
from dump.common_onenand_id import CommonOnenandId


class NecOnenandId_v2(CommonOnenandId, RwAccess_v2, NecProtocol_v2):
    pass
