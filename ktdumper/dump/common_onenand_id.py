import struct


deviceid_vcc = {
    0: "1.8V",
    1: "3.3V",
    2: "reserved",
    3: "reserved",
}

deviceid_muxed = {
    0: "Muxed",
    1: "Demuxed",
}

deviceid_ddp = {
    0: "Single",
    1: "DDP",
}

deviceid_density = {
    0: "16MB",
    1: "32MB",
    2: "64MB",
    3: "128MB",
    4: "256MB",
    5: "512MB",
    6: "1GB",
    7: "2GB",
}

deviceid_separation = {
    0b00: "SLC",
    0b01: "MLC",
    0b10: "Flex",
    0b11: "Reserved",
}


class CommonOnenandId:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.onenand_addr = opts["onenand_addr"]

        self.onenand_MANU_ID = self.onenand_addr + 2*0xF000
        self.onenand_DEVICE_ID = self.onenand_addr + 2*0xF001
        self.onenand_TECHNOLOGY = self.onenand_addr + 2*0xF006
        self.onenand_DATA_BUFFER_SIZE = self.onenand_addr + 2*0xF003
        self.onenand_BOOT_BUFFER_SIZE = self.onenand_addr + 2*0xF004
        self.onenand_AMOUNT_OF_BUFFERS = self.onenand_addr + 2*0xF005

        self.onenand_REG_START_ADDRESS1 = self.onenand_addr + 2*0xF100
        self.onenand_REG_START_ADDRESS2 = self.onenand_addr + 2*0xF101
        self.onenand_REG_START_ADDRESS8 = self.onenand_addr + 2*0xF107
        self.onenand_REG_START_BUFFER = self.onenand_addr + 2*0xF200
        self.onenand_REG_INTERRUPT = self.onenand_addr + 2*0xF241
        self.onenand_REG_COMMAND = self.onenand_addr + 2*0xF220
        self.onenand_DATARAM = self.onenand_addr + 2*0x200
        self.onenand_SPARERAM = self.onenand_addr + 2*0x8010
        self.onenand_SYSCFG1 = self.onenand_addr + 2*0xF221

        self.onenand_DATARAM = self.onenand_addr + 2*0x200

    def _read_pi_page(self, ddp, page):
        ddp_bit = ddp << 15

        # disable ECC
        prev_syscfg = self.readh(self.onenand_SYSCFG1)
        self.writeh(prev_syscfg | 0x100, self.onenand_SYSCFG1)

        # enter PI mode
        self.writeh(ddp_bit, self.onenand_REG_START_ADDRESS1)
        self.writeh(ddp_bit, self.onenand_REG_START_ADDRESS2)
        self.writeh(0, self.onenand_REG_INTERRUPT)
        self.writeh(0x66, self.onenand_REG_COMMAND)

        while True:
            reg = self.readh(self.onenand_REG_INTERRUPT)
            if reg & 0x8000:
                break
        assert reg == 0x8000

        # read the page
        self.writeh(page << 2, self.onenand_REG_START_ADDRESS8)
        self.writeh((1 << 3) << 8, self.onenand_REG_START_BUFFER)
        self.writeh(0, self.onenand_REG_INTERRUPT)
        self.writeh(0x00, self.onenand_REG_COMMAND)

        while True:
            reg = self.readh(self.onenand_REG_INTERRUPT)
            if reg & 0x8000:
                break
        assert reg == 0x8080

        page = self.read(self.onenand_DATARAM, 4096)

        # perform a nand core reset to exit PI mode
        self.writeh(0, self.onenand_REG_INTERRUPT)
        self.writeh(0xF0, self.onenand_REG_COMMAND)
        while True:
            reg = self.readh(self.onenand_REG_INTERRUPT)
            if reg & 0x8000:
                break
        assert reg == 0x8010

        # re-enable ECC
        self.writeh(prev_syscfg, self.onenand_SYSCFG1)

        return page

    def print_pi(self, ddp):
        pi = b""
        for page in range(64):
            pi += self._read_pi_page(ddp, page)

        assert pi[2:len(pi)] == b"\xFF" * (len(pi) - 2)
        alloc = struct.unpack("<H", pi[0:2])[0]
        print("DDP {} : Allocation 0x{:04X}".format(ddp, alloc))
        # datasheet default: 0xFC00, seen: 0xF800 (same behavior?)

    def execute(self, dev, output):
        super().execute(dev, output)

        manu_id = self.readh(self.onenand_MANU_ID)
        print("Manufacturer ID: {:04X}".format(manu_id))
        print("")

        device_id = self.readh(self.onenand_DEVICE_ID)
        print("DeviceID: {:04X}".format(device_id))
        vcc = device_id & 0b11
        muxed = (device_id >> 2) & 0b1
        ddp = (device_id >> 3) & 0b1
        density = (device_id >> 4) & 0b111
        separation = (device_id >> 8) & 0b11
        print("* DeviceID [1:0]  Vcc:           {:02b}  = {}".format(vcc, deviceid_vcc[vcc]))
        print("* DeviceID [2]    Muxed/Demuxed: {:0b}   = {}".format(muxed, deviceid_muxed[muxed]))
        print("* DeviceID [3]    Single/DDP:    {:0b}   = {}".format(ddp, deviceid_ddp[ddp]))
        print("* DeviceID [6:4]  Density:       {:03b} = {}".format(density, deviceid_density[density]))
        print("* DeviceID [9:8]  Separation:    {:02b}  = {}".format(separation, deviceid_separation[separation]))

        print("")
        print("Technology: {:04X}".format(self.readh(self.onenand_TECHNOLOGY)))
        print("Data Buffer Size: {:04X}".format(self.readh(self.onenand_DATA_BUFFER_SIZE)))
        print("Boot Buffer Size: {:04X}".format(self.readh(self.onenand_BOOT_BUFFER_SIZE)))
        print("Amount of Buffers: {:04X}".format(self.readh(self.onenand_AMOUNT_OF_BUFFERS)))

        print("")
        print("System Configuration 1: {:04X}".format(self.readh(self.onenand_SYSCFG1)))
        print("")

        if manu_id not in [0xEC, 0x20]:
            raise RuntimeError("OneNAND manufacturer ID isn't 00ECh or 0020h")

        if separation == 2:
            print("=" * 80)
            print("Readout Partition Information")
            print("=" * 80)
            for x in range(ddp + 1):
                self.print_pi(x)
