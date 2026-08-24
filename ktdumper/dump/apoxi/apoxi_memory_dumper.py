from dump.apoxi.apoxi_protocol import ApoxiProtocol
from dump.common.common_memory_dumper import CommonMemoryDumper


class ApoxiMemoryDumper(CommonMemoryDumper, ApoxiProtocol):
    mem_chunk = 0x80
