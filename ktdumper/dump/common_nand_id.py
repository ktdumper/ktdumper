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

    def execute(self, dev, output):
        super().execute(dev, output)

        nand_id = self.read_id()

        print("=" * 80)
        print("NAND ID : {}".format(nand_id.hex()))
        print("ONFI    : {}".format(self.read_onfi().hex()))
        print("=" * 80)

        # Spansion
        if nand_id[0] == 0x01:
            print("Maker Code                                     : {:02X} (Spansion)".format(nand_id[0]))
            print("Device Code 1st Byte                           : {:02X} ({})".format(nand_id[2], spansion_device_code.get(nand_id[2], "UNKNOWN")))
            print("Device Code 2nd Byte                           : {:02X}".format(nand_id[4]))
            print("Block Size, Simultaneous Programmed Pages, RFU : {:02X}".format(nand_id[6]))
            print("Page Size, Spare Size, RFU                     : {:02X}".format(nand_id[8]))
            # print("RAM and Other MCP identifiers                  : {:02X}".format(nand_id[10]))
