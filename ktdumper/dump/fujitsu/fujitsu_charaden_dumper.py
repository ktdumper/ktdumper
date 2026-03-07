from dump.fujitsu.fujitsu_protocol import FujitsuProtocol

class FujitsuCharadenDumper(FujitsuProtocol):

    def execute(self, dev, output):
        super().execute(dev, output)
        list_info = [
            ("Preinstall", "FFFFFFFFFFFFFFFFFFFF"),
            ("Imode", "8981100010318677060F"),
        ]
        for folder, serial in list_info:
            for x in range(32):
                file_data = self.retrieve_file(f"D:\\Sanremo\\Media\\FjmmAvatar\\Data\\{folder}\\{x}_{serial}.AFD")
                if file_data is not None:
                    with self.output.mkfile(f"{folder}/{x}_{serial}.afd") as outf:
                        outf.write(file_data)