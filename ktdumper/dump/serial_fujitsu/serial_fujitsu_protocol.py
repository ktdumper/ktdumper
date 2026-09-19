import struct
import time

import serial

from dump.dumper import Dumper


class SerialFujitsuProtocol(Dumper):

    def connect(self, dev):
        self.port = serial.Serial(dev, 600, parity='E', rtscts=True,
                                  timeout=0.02, write_timeout=5, exclusive=True)
        self.port.dtr = True
        self.port.rts = True
        self.binary = False
        self.service_mode()

    def send(self, packet):
        for byte in packet:
            self.port.write(bytes([byte]))
            time.sleep(0.00025 if self.port.baudrate == 115200 else 0.021)

    def receive(self, size):
        reply = bytearray()
        while len(reply) < size:
            reply += self.port.read(size - len(reply))
        return bytes(reply)

    def receive_until(self, suffix):
        reply = bytearray()
        while not reply.endswith(suffix):
            reply += self.port.read(1)
        return bytes(reply)

    def service_mode(self):
        print('Entering service mode...', flush=True)
        time.sleep(2)
        self.port.reset_input_buffer()
        self.send(b'\xd1\x02\x0f')
        reply = self.receive_until(b'>')
        assert b'DEBUGER' in reply or b'BREAK AT' in reply
        self.send(b'B 1152\r')
        self.receive_until(b'B 1152\r')
        self.port.baudrate = 115200
        time.sleep(0.2)
        self.port.reset_input_buffer()
        self.send(b'\r')
        self.receive_until(b'>')

    def set_binary(self, enabled):
        if enabled != self.binary:
            self.send(b'Z\r' if enabled else b'Z')
            self.receive_until(b'BIN MODE\r\n' if enabled else b'>')
            self.binary = enabled

    def command(self, text):
        self.set_binary(False)
        packet = text.encode('ascii')
        assert all(32 <= byte <= 126 for byte in packet)
        self.send(packet)
        if self.receive(len(packet)) != packet:
            raise ValueError('Command echo mismatch')
        self.port.write(b'\r')
        return self.receive_until(b'\r\n>')

    def read_flash(self, address, size):
        self.set_binary(True)
        request = b'R' + struct.pack('>II', address, size)
        self.send(request)
        reply = self.receive(len(request))
        if reply != request:
            raise ValueError(f'Unexpected reply: {reply.hex()}')
        data = self.receive(size + 1)
        if sum(data) & 255:
            raise ValueError('Memory read checksum mismatch')
        return data[:-1]

    def disconnect(self):
        self.set_binary(False)
        self.send(b'Q\r')
        time.sleep(2)
        self.port.close()
