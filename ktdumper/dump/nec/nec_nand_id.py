from dump.nec.nec_protocol import NecProtocol
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess
from dump.common.common_nand_id import CommonNandId


class NecNandId(CommonNandId, NecPiplRwAccess, NecProtocol):
    pass
