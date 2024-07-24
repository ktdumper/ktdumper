import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.nec_pipl_rw_access import NecPiplRwAccess
from dump.common_nand_id import CommonNandId


class NecNandId(CommonNandId, NecPiplRwAccess, NecProtocol):
    pass
