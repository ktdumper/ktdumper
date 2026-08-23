import zlib
import struct


class CommonChunkedProtocol:

    def mask_packet(self, pkt):
        out = []
        for ch in pkt:
            if ch in [0xFF, 0xFE]:
                out.append(0xFE)
                out.append(ch ^ 0x10)
            else:
                out.append(ch)
        out.append(0xFF)
        return bytearray(out)


    def unmask_resp(self, resp):
        out = []
        x = 0
        while x < len(resp):
            if resp[x] == 0x99:
                out.append(resp[x+1] ^ 0x10)
                x += 2
            else:
                out.append(resp[x])
                x += 1
        return bytearray(out)

    def usb_send(self, data):
        ck = (-sum(data)) & 0xFF
        pkt = self.mask_packet(bytearray(data) + bytes([ck]))
        assert self.dev.write(self.ep_tx, pkt) == len(pkt)

    def _usb_readch(self):
        while not len(self.buffer):
            resp = self.dev.read(self.ep_rx, 64)
            for b in resp:
                self.buffer.append(b)

        return self.buffer.pop(0)

    def usb_receive(self):
        resp = []

        over = False
        while not over:
            # start retrieving chunk, first ch=9B
            ch = self._usb_readch()
            assert ch == 0x9B

            # retrieve body of the chunk
            while True:
                ch = self._usb_readch()

                # 9D = chunk is over
                if ch == 0x9D:
                    # SYNC
                    self.dev.write(self.ep_tx, b"\xAA")
                    break
                # 9C = whole payload is over
                elif ch == 0x9C:
                    over = True
                    break
                # 9A = padding
                elif ch == 0x9A:
                    pass
                else:
                    resp.append(ch)

        data = bytearray(self.unmask_resp(resp))
        # print("<= {}".format(data.hex()))

        # checksum is the last 4 bytes
        crc = struct.unpack("<I", data[-4:])[0]
        assert zlib.crc32(data[:-4]) == crc

        return data[:-4]
