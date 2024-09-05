import struct

from dump.nec.nec_direct_usb import NecDirectUsb
from dump.common_memory_dumper import CommonMemoryDumper


class NecMemoryDumperPayloadExec:

    def read(self, addr, sz):
        self.comm(3, variable_payload=struct.pack("<BIH", 1, addr, sz))
        data = self.read_resp()
        assert len(data) == sz + 10
        return data[9:-1]

    def execute(self, dev, output):
        super().execute(dev, output)

        print("!! Restart the phone before running another payload !!")
        self.insert_payload("memory_read.c")


class NecMemoryDumperPayload(CommonMemoryDumper, NecMemoryDumperPayloadExec, NecDirectUsb):

    mem_chunk = 0x10
