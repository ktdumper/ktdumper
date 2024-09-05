SIZES = [0, 32, 64, 96, 128, 256]
OFFSETS = [0, 0x100, 0x9000, 0x17000, 0x23000, 0x46000]


class CommonNorProbe:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.base = opts["base"]

    def execute(self, dev, output):
        super().execute(dev, output)

        for sz in SIZES:
            print("=" * 80)
            print("at {} MiB".format(sz))
            print("=" * 80)

            if sz != 0:
                for off in OFFSETS[::-1]:
                    if off == 0:
                        continue
                    blk = self.read(self.base + sz * 1024 * 1024 - off, 64)
                    print("-0x{:08X} : {}".format(off, blk.hex()))

            for off in OFFSETS:
                blk = self.read(self.base + sz * 1024 * 1024 + off, 64)
                print("+0x{:08X} : {}".format(off, blk.hex()))

            print("")
