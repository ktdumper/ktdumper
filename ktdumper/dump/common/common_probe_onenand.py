from dump.common.common_onenand_id import ONENAND_KNOWN_MANU


class CommonProbeOnenand:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.sweep_start = opts["sweep_start"]

    def read_id(self, base):
        onenand_MANU_ID = base + 2*0xF000
        onenand_DEVICE_ID = base + 2*0xF001

        manu_id = self.readh(onenand_MANU_ID)
        device_id = self.readh(onenand_DEVICE_ID)

        s = "MID : 0x{:04X} | DID : 0x{:04X}".format(manu_id, device_id)
        if manu_id in ONENAND_KNOWN_MANU:
            s += " => possible match; boot data={}...".format(self.read(base, 64).hex())
        return s

    def execute(self, dev, output):
        super().execute(dev, output)

        for addr in range(self.sweep_start, 2**32, 0x01000000):
            print("0x{:08X} :: {}".format(addr, self.read_id(addr)))
