from dump.nec_protocol_v2 import NecProtocol_v2
from dump.nec_rw_access_v2 import NecRwAccess_v2
from dump.onenand_fast_v2 import OnenandFast_v2

class NecOnenandFast_v2(OnenandFast_v2, NecRwAccess_v2, NecProtocol_v2):
    pass
