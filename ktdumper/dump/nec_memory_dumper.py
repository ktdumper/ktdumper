import tqdm

from dump.nec_protocol import NecProtocol
from dump.common_memory_dumper import CommonMemoryDumper


class NecMemoryDumper(CommonMemoryDumper, NecProtocol):
    pass
