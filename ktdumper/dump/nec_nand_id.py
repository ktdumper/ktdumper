import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.common_rw_access import CommonRwAccess
from dump.common_nand_id import CommonNandId


class NecNandId(CommonNandId, CommonRwAccess, NecProtocol):
    pass
