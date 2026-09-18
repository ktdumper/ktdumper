import time

import serial

from dump.dumper import Dumper


class SerialNecProtocol(Dumper):

    def connect(self, dev):
        self.port = serial.Serial(dev, 600, parity='E', rtscts=True,
                                  timeout=0.02, write_timeout=5, exclusive=True)
        self.service_mode()

    def send(self, packet):
        for byte in packet:
            self.port.write(bytes([byte]))
            time.sleep(0.0006 if self.port.baudrate == 115200 else 0.021)
        self.port.flush()

    def receive(self, header, size=0):
        reply = bytearray()
        count = len(header) + size
        while len(reply) < count:
            for byte in self.port.read(count - len(reply)):
                if 0xc0 <= byte <= 0xcf:
                    continue
                if not reply and byte in (0xa8, 0xa9):
                    continue
                reply.append(byte)
                if len(reply) <= len(header) and byte != header[len(reply) - 1]:
                    raise ValueError(f'Unexpected reply: {reply.hex()}')
        if self.port.baudrate != 115200:
            time.sleep(0.06)
        return reply[len(header):]

    def service_mode(self):
        print('Entering service mode...', flush=True)
        for baud in (600, 115200, 38400, 2400, 9600):
            self.port.baudrate = baud
            for attempt in range(2):
                try:
                    self.send(b'\x1e\x06\x0c')
                    self.receive(b'\x1e\x01\x02')
                except (TimeoutError, ValueError):
                    if attempt == 0:
                        time.sleep(15)
                    self.port.reset_input_buffer()
                    continue
                if baud != 115200:
                    self.send(b'\xd1\x06\x0b\x00\x00\x06\x00')
                    self.port.baudrate = 115200
                    self.receive(b'\xd1\x06\x0b\x00')
                return
        raise RuntimeError('cannot enter service mode')

    @staticmethod
    def nibbles(value, count):
        return bytes((value >> (4 * i)) & 15 for i in reversed(range(count)))

    def read_flash(self, request, size):
        self.send(request)
        data = self.receive(request, size * 2)
        if any(byte > 15 for byte in data):
            raise ValueError('Invalid flash data')
        return bytes((a << 4) | b for a, b in zip(data[::2], data[1::2]))
