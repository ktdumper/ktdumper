import time

import serial

from dump.dumper import Dumper


def exit_service_mode(port):
    for byte in b'\x1f\x07\x0d':
        port.write(bytes([byte]))
        time.sleep(0.0006 if port.baudrate == 115200 else 0.021)
    port.flush()


class SerialNecExitServiceMode(Dumper):

    def execute(self, dev, output):
        with serial.Serial(dev, 115200, parity='E', rtscts=True) as port:
            exit_service_mode(port)
