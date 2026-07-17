import time

from dump.dumper import Dumper


def mask_packet(pkt):
    out = [0xFF]
    for b in pkt:
        if b in [0xFD, 0xFE, 0xFF]:
            out.append(0xFD)
            out.append(b ^ 0x10)
        else:
            out.append(b)
    out.append(0xFE)

    return bytearray(out)

def unmask_resp(resp):
    assert resp[0] == 0xFF
    assert resp[-1] == 0xFE
    resp = resp[1:-1]
    out = []
    x = 0
    while x < len(resp):
        if resp[x] == 0xFD:
            out.append(resp[x+1] ^ 0x10)
            x += 2
        else:
            out.append(resp[x])
            x += 1
    return bytearray(out)


class FujitsuProtocol(Dumper):

    def init_maker_mode(self):
        # validate support for setting ep mode=0xC0
        self.dev.ctrl_transfer(0x41, 0x62, 0x00, 0x00, b"\x02\xC0")
        self.dev.read(0x81, 256)

        # change ep to mode=0xC0
        self.dev.ctrl_transfer(0x41, 0x60, 0xC0, 0x00)
        self.dev.read(0x81, 256)

        # enter maker mode
        self.dev.write(3, bytes.fromhex("FF 56 55 42 00 03 C1 01 00 FE"))
        self.dev.read(0x82, 256)

        # wait for the system to come up
        maker_mode = False
        for x in range(60):
            print("Waiting for maker mode {}s...".format(x))
            time.sleep(1)

            try:
                payload = b"\xC6\x13\x00" + b"z:\\does_not_exist"
                pkt = mask_packet(b"\x55\x56\x42" + len(payload).to_bytes(2, byteorder="big") + payload)
                self.dev.write(3, pkt)
                data = unmask_resp(bytearray(self.dev.read(0x82, 4096)))
            except Exception as e:
                continue

            if data[7] == 0xA1:
                maker_mode = True
                break
        if not maker_mode:
            raise RuntimeError("Failed to enter maker mode")
        print("Entered maker mode successfully")

    def retrieve_file(self, device_path):
        payload = b"\xC6\x13\x00" + device_path.encode("ascii")
        assert len(payload) < 2 ** 16
        pkt = mask_packet(b"\x55\x56\x42" + len(payload).to_bytes(2, byteorder="big") + payload)
        self.dev.write(3, pkt)

        output = b""
        while True:
            data = unmask_resp(bytearray(self.dev.read(0x82, 4096)))

            # file not found
            if data[7] == 0xA1:
                return None

            chk = sum(data[9:])
            assert data[8] == chk & 0xFF

            output += data[9:]

            if data[7] == 0x91:
                break

            payload = b"\xC6\x13\x20"
            pkt = mask_packet(b"\x55\x56\x42" + len(payload).to_bytes(2, byteorder="big") + payload)
            self.dev.write(3, pkt)
        return output
        
    def ls(self, dir_path):
        cmd_bytes = b"\xC6\x13\x31"
        if dir_path[-1] != "\\":
            dir_path += "\\"

        payload = cmd_bytes + dir_path.encode("ascii")

        pkt = mask_packet(b"\x55\x56\x42" + len(payload).to_bytes(2, byteorder="big") + payload)
        self.dev.write(3, pkt)
        
        response_buf = bytearray()
        
        while True:
            resp = unmask_resp(bytearray(self.dev.read(0x82, 4096)))
            response_buf += resp[8:]

            if resp[7] == 0x91:
                ls_str = response_buf.decode("cp932", errors="replace")
                return ls_str.split(",")[:-1]

            payload = b"\xC6\x13\x20"
            pkt = mask_packet(b"\x55\x56\x42" + len(payload).to_bytes(2, byteorder="big") + payload)
            self.dev.write(3, pkt)

    def get_file_paths_deep(self, dir_path):
        file_paths = []
        
        def recursive(_dir):
            for p in self.ls(_dir):
                abs_path = _dir + p
                if p[-1] == "\\":
                    recursive(abs_path)
                else:
                    file_paths.append(abs_path)

        recursive(dir_path)
        
        return file_paths


    def execute(self, dev, output):
        self.dev = dev
        self.output = output

        self.init_maker_mode()
