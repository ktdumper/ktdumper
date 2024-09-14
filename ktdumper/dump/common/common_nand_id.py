import struct


spansion_device_code = {
    0x81: "64MB (x8)",
    0x91: "64MB (x16)",
    0xA1: "128MB (x8)",
    0xB1: "128MB (x16)",
    0xAA: "256MB (x8)",
    0xBA: "256MB (x16)",
    0xCC: "512MB (x8)",
    0xDC: "512MB (x16)",
}

micron_device_code = {
    0xDC: "4Gb, x8, 3.3V",
    0xCC: "4Gb, x16, 3.3V",
    0xAC: "4Gb, x8, 1.8V",
    0xBC: "4Gb, x16, 1.8V",
    0xA3: "8Gb, x8, 1.8V",
    0xB3: "8Gb, x16, 1.8V",
    0xD3: "8Gb, x8, 3.3V",
    0xC3: "8Gb, x16, 3.3V",
    0xD3: "16Gb, x8, 3.3V",
}

class CommonNandId:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.NAND_CMD = opts["nand_cmd"]
        self.NAND_ADDR = opts["nand_addr"]
        self.NAND_DATA = opts["nand_data"]

    def read_id(self):
        self.writeb(0x90, self.NAND_CMD)
        self.writeb(0x00, self.NAND_ADDR)
        ret = b""
        for x in range(5):
            h = self.readh(self.NAND_DATA)
            ret += bytes([h & 0xFF, (h >> 8) & 0xFF])
        return ret

    def read_onfi(self):
        self.writeb(0x90, self.NAND_CMD)
        self.writeb(0x20, self.NAND_ADDR)
        ret = b""
        for x in range(5):
            h = self.readh(self.NAND_DATA)
            ret += bytes([h & 0xFF, (h >> 8) & 0xFF])
        return ret

    def print_onfi(self):
        print("=" * 80)
        print("ONFI")
        print("=" * 80)

        self.writeb(0xEC, self.NAND_CMD)
        self.writeb(0x00, self.NAND_ADDR)

        onfi = b""
        for x in range(256):
            h = 0xffff
            while h == 0xffff:
                h = self.readh(self.NAND_DATA)
            assert h < 0x100
            onfi += bytes([h])

        assert onfi[0:4] == b"ONFI"

        print("Device manufacturer: {}".format(onfi[32:44].decode("ascii")))
        print("Device model: {}".format(onfi[44:64].decode("ascii")))
        print("JEDEC manufacturer ID: {:02X}h".format(onfi[64]))
        print("-" * 80)
        print("Number of data bytes per page: {}".format(struct.unpack("<I", onfi[80:84])[0]))
        print("Number of spare bytes per page: {}".format(struct.unpack("<H", onfi[84:86])[0]))
        print("Number of pages per block: {}".format(struct.unpack("<I", onfi[92:96])[0]))
        print("Number of blocks per logical unit (LUN): {}".format(struct.unpack("<I", onfi[96:100])[0]))
        print("Number of logical units (LUNs): {}".format(onfi[100]))
        print("-" * 80)
        total_size = struct.unpack("<I", onfi[80:84])[0] * struct.unpack("<I", onfi[92:96])[0] * struct.unpack("<I", onfi[96:100])[0] * onfi[100]
        total_size /= 1024 * 1024
        print("Calculated total size (excl spare): {:.2f} MB".format(total_size))

    def execute(self, dev, output):
        super().execute(dev, output)

        nand_id = self.read_id()
        onfi_id = self.read_onfi()

        print("=" * 80)
        print("NAND ID : {}".format(nand_id.hex()))
        print("ONFI    : {}".format(onfi_id.hex()))

        # Spansion
        if nand_id[0] == 0x01:
            print("=" * 80)
            print("Maker Code                                     : {:02X} (Spansion)".format(nand_id[0]))
            print("Device Code 1st Byte                           : {:02X} ({})".format(nand_id[2], spansion_device_code.get(nand_id[2], "UNKNOWN")))
            print("Device Code 2nd Byte                           : {:02X}".format(nand_id[4]))
            print("Block Size, Simultaneous Programmed Pages, RFU : {:02X}".format(nand_id[6]))
            print("Page Size, Spare Size, RFU                     : {:02X}".format(nand_id[8]))
            # print("RAM and Other MCP identifiers                  : {:02X}".format(nand_id[10]))
        # Micron
        elif nand_id[0] == 0x2C:
            print("=" * 80)
            print("Maker Code                                     : {:02X} (Micron)".format(nand_id[0]))
            print("Device ID                                      : {:02X} ({})".format(nand_id[2], micron_device_code.get(nand_id[2], "UNKNOWN")))

        if onfi_id == bytes.fromhex("4f004e00460049004900"):
            self.print_onfi()
