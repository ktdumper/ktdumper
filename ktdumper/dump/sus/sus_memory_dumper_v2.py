from dump.common.common_memory_dumper import CommonMemoryDumper
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.sus.sus_exploit_v2 import SusExploit_v2


class SusMemoryDumper_v2(CommonMemoryDumper, RwAccess_v2, SusExploit_v2):
    supports_2048 = True
