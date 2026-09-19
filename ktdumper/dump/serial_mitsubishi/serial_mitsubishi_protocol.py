import time

import serial

from dump.dumper import Dumper


class SerialMitsubishiProtocol(Dumper):

    def connect(self, dev):
        self.port = serial.Serial(dev, 600, parity='E', rtscts=True,
                                  timeout=0.02, write_timeout=5, exclusive=True)
        self.port.dtr = True
        self.port.rts = True
        self.service_mode()

    def send(self, packet):
        for byte in packet:
            if self.port.write(bytes([byte])) != 1:
                raise IOError('Short serial write')
            time.sleep(0.0005 if self.port.baudrate == 115200 else 0.021)
        self.port.flush()

    def receive(self, size):
        reply = bytearray()
        while len(reply) < size:
            reply += self.port.read(size - len(reply))
        return bytes(reply)

    @staticmethod
    def nibbles(value, count):
        return bytes((value >> (4 * i)) & 15 for i in reversed(range(count)))

    @staticmethod
    def decode(data):
        value = 0
        for byte in data:
            if byte > 15:
                raise ValueError('Invalid nibble data')
            value = (value << 4) | byte
        return value

    def packet(self, command, data=b''):
        return b'\xd1\x03\x09' + self.nibbles(command, 2) + self.nibbles(len(data), 4) + data

    def exchange(self, request, command, size):
        self.send(request)
        while True:
            prefix = b''
            while prefix != b'\xd1\x03\x09':
                prefix = (prefix + self.receive(1))[-3:]
            header = prefix + self.receive(6)
            length = self.decode(header[5:9])
            if length > 0x800:
                raise ValueError(f'Unexpected reply length: {length}')
            data = self.receive(length)
            if header + data == request:
                continue
            if self.decode(header[3:5]) != command:
                continue
            if length != size:
                raise ValueError(f'Unexpected reply: {header.hex()} {data.hex()}')
            return data

    def enter(self):
        self.exchange(self.packet(0, bytes.fromhex('04 04 01 00 05 03 03 01 00 00 00')), 0, 0)

    def service_mode(self):
        print('Entering service mode...', flush=True)
        self.enter()
        self.set_baud(115200)

    def set_baud(self, baud):
        assert baud in (600, 115200)
        if baud == self.port.baudrate:
            return
        data = self.nibbles(0x148, 4) + self.nibbles(0x13, 4) + self.nibbles(0x13, 4)
        data += self.nibbles(baud, 8) + self.nibbles(0, 8)
        request = self.packet(0x10, data)
        self.send(request)
        time.sleep(0.75)
        self.port.baudrate = baud
        time.sleep(0.15)
        self.port.reset_input_buffer()
        self.enter()

    def read_flash(self, address, size):
        assert 2 <= size <= 255
        request = self.packet(0x0c, self.nibbles(address, 8) + self.nibbles(size, 2))
        data = self.exchange(request, 0x0c, 8 + size * 2)
        if self.decode(data[:8]) != address:
            raise ValueError('Memory read address mismatch')
        return bytes(self.decode(data[i:i + 2]) for i in range(8, len(data), 2))
