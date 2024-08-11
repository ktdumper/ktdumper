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
        print("* DeviceID [1:0]  Vcc:           {:02b}  = {}".format(vcc, deviceid_vcc[vcc]))
        print("* DeviceID [2]    Muxed/Demuxed: {:0b}   = {}".format(muxed, deviceid_muxed[muxed]))
        print("* DeviceID [3]    Single/DDP:    {:0b}   = {}".format(ddp, deviceid_ddp[ddp]))
        print("* DeviceID [6:4]  Density:       {:03b} = {}".format(density, deviceid_density[density]))

        print("")
        print("Technology: {:04X}".format(self.readh(self.onenand_TECHNOLOGY)))
        print("Data Buffer Size: {:04X}".format(self.readh(self.onenand_DATA_BUFFER_SIZE)))
        print("Boot Buffer Size: {:04X}".format(self.readh(self.onenand_BOOT_BUFFER_SIZE)))
        print("Amount of Buffers: {:04X}".format(self.readh(self.onenand_AMOUNT_OF_BUFFERS)))

        print("")
        print("System Configuration 1: {:04X}".format(self.readh(self.onenand_addr + 2*0xF221)))

        if manu_id != 0xEC:
            raise RuntimeError("OneNAND manufacturer ID isn't 00ECh")
