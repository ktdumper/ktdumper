import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.nec_rw_access_v2 import NecRwAccess_v2
from dump.common_onenand_id import CommonOnenandId


class NecOnenandId_v2(CommonOnenandId, NecRwAccess_v2, NecProtocol):
    pass
