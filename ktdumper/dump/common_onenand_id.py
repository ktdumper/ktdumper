from dump.common_rw_access import CommonRwAccess


class CommonOnenandId(CommonRwAccess):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.onenand_addr = opts["onenand_addr"]

        self.onenand_MANU_ID = self.onenand_addr + 2*0xF000
        self.onenand_DEVICE_ID = self.onenand_addr + 2*0xF001
        self.onenand_TECHNOLOGY = self.onenand_addr + 2*0xF006
        self.onenand_DATA_BUFFER_SIZE = self.onenand_addr + 2*0xF003
        self.onenand_BOOT_BUFFER_SIZE = self.onenand_addr + 2*0xF004
        self.onenand_AMOUNT_OF_BUFFERS = self.onenand_addr + 2*0xF005

    def execute(self, dev, output):
        super().execute(dev, output)

        print("Manufacturer ID: {:04X}".format(self.readh(self.onenand_MANU_ID)))
        print("Device ID: {:04X}".format(self.readh(self.onenand_DEVICE_ID)))
        print("Technology: {:04X}".format(self.readh(self.onenand_TECHNOLOGY)))
        print("Data Buffer Size: {:04X}".format(self.readh(self.onenand_DATA_BUFFER_SIZE)))
        print("Boot Buffer Size: {:04X}".format(self.readh(self.onenand_BOOT_BUFFER_SIZE)))
        print("Amount of Buffers: {:04X}".format(self.readh(self.onenand_AMOUNT_OF_BUFFERS)))
