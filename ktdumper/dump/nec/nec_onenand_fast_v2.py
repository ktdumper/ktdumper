from dump.nec.nec_protocol_v2 import NecProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.v2.onenand_fast_v2 import OnenandFast_v2

class NecOnenandFast_v2(OnenandFast_v2, RwAccess_v2, NecProtocol_v2):
    pass
