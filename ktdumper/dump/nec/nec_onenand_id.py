from dump.nec.nec_protocol import NecProtocol
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess
from dump.common.common_onenand_id import CommonOnenandId


class NecOnenandId(CommonOnenandId, NecPiplRwAccess, NecProtocol):
    pass
