import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.nec_pipl_rw_access import NecPiplRwAccess
from dump.common_onenand_id import CommonOnenandId


class NecOnenandId(CommonOnenandId, NecPiplRwAccess, NecProtocol):
    pass
