from dump.mlc_check_v2 import MlcCheck_v2
from dump.nec_protocol_v2 import NecProtocol_v2
from dump.rw_access_v2 import RwAccess_v2


class NecMlcCheck(MlcCheck_v2, RwAccess_v2, NecProtocol_v2):
    pass
