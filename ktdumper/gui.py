from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QWidget, QGroupBox, QScrollBar, QSizePolicy, QAction
from PyQt5.QtGui import QWindow, QKeyEvent
from PyQt5.QtCore import QProcess, QIODevice, Qt, QBuffer, QTimer
from QTermWidget import QTermWidget
import sys
import git
import subprocess
import usb.core
import os
import signal

from devices import DEVICES


KTDUMPERLIVEOUTPUT = "/tmp/ktdumperliveoutput"


def get_git_version():
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha


def noop(*args, **kwargs):
    pass


class ReadonlyTerminal(QTermWidget):

    def __init__(self, process, args):
        super().__init__(0)
        self.finished.connect(self.close)
        self.setTerminalSizeHint(False)
        self.setColorScheme("DarkPastels")
        self.setShellProgram(process)
        self.setArgs(args)
        self.startShellProgram()

        self.layout().itemAt(0).widget().keyPressedSignal.disconnect()
        self.setScrollBarPosition(2)

        self.copy_action = QAction("&Copy", self)
        self.copy_action.triggered.connect(self.on_copy)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addAction(self.copy_action)

    def on_copy(self):
        buf = QBuffer()
        buf.open(QBuffer.ReadWrite)
        self.saveHistory(buf)

        text = buf.data().data().decode("utf-8", errors="ignore")
        QApplication.clipboard().setText(text.strip())


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.process = None

        self.setWindowTitle("ktdumper revision {}".format(get_git_version()))

        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(1000)
        self.refresh_timer.timeout.connect(self.on_refresh_timer)
        self.refresh_timer.start()

        layout = QVBoxLayout()

        dumper_layout = QHBoxLayout()
        dumper_layout.addStretch()
        dumper_layout.addWidget(QLabel("Device:"))
        self.cmb_devices = QComboBox()
        self.cmb_devices.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmb_devices.currentIndexChanged.connect(self.update_payloads)
        dumper_layout.addWidget(self.cmb_devices)
        dumper_layout.addWidget(QLabel("Payload:"))
        self.cmb_payloads = QComboBox()
        self.cmb_payloads.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        dumper_layout.addWidget(self.cmb_payloads)
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.on_start)
        dumper_layout.addWidget(start_btn)
        dumper_layout.addStretch()
        self.dumper = QGroupBox()
        self.dumper.setLayout(dumper_layout)
        self.dumper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        layout.addWidget(self.dumper)

        interrupt_layout = QHBoxLayout()
        interrupt_layout.addStretch()
        interrupt_btn = QPushButton("Interrupt")
        interrupt_btn.clicked.connect(self.on_interrupt)
        interrupt_layout.addWidget(interrupt_btn)
        interrupt_layout.addStretch()
        self.interrupt = QGroupBox()
        self.interrupt.setLayout(interrupt_layout)
        self.interrupt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        layout.addWidget(self.interrupt)
        self.interrupt.hide()

        with open(KTDUMPERLIVEOUTPUT, "w") as outf:
            outf.write("Waiting for command...\n")

        w = ReadonlyTerminal("tail", ["-f", KTDUMPERLIVEOUTPUT])
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setVerticalStretch(3)
        w.setSizePolicy(size_policy)
        layout.addWidget(w)

        system_layout = QHBoxLayout()
        lsusb_group = QGroupBox("lsusb")
        l = QHBoxLayout()
        l.addWidget(ReadonlyTerminal("watch", ["-n", "1", "-c", "-t",
            "cyme", "--encoding", "utf8", "--hide-buses", "--hide-hubs", "-b", "vendor-id", "-b", "product-id", "-b", "name", "-b", "bcd-usb"]))
        lsusb_group.setLayout(l)
        dmesg_group = QGroupBox("dmesg")
        l = QHBoxLayout()
        l.addWidget(ReadonlyTerminal("dmesg", ["-w"]))
        dmesg_group.setLayout(l)
        system_layout.addWidget(lsusb_group)
        system_layout.addWidget(dmesg_group)

        w = QWidget()
        w.setLayout(system_layout)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setVerticalStretch(5)
        w.setSizePolicy(size_policy)
        layout.addWidget(w)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.update_devices()

        self.show()

    def valid_device_payload(self, device, payload):
        for dev in DEVICES:
            if dev.name == device:
                return payload in dev.commands
        return False

    def on_start(self):
        device_name = self.cmb_devices.currentText()
        payload_name = self.cmb_payloads.currentText()

        if self.process is None and self.valid_device_payload(device_name, payload_name):
            self.process = QProcess()
            self.process.finished.connect(self.on_finish)
            self.process.setStandardOutputFile(KTDUMPERLIVEOUTPUT, QIODevice.Append)
            self.process.setStandardErrorFile(KTDUMPERLIVEOUTPUT, QIODevice.Append)
            self.process.start("python3", ["-u", "ktdumper/ktdumper.py", device_name, payload_name])
            self.dumper.hide()
            self.interrupt.show()

    def on_finish(self):
        self.process = None
        self.interrupt.hide()
        self.dumper.show()

    def on_interrupt(self):
        if self.process is not None:
            os.kill(self.process.processId(), signal.SIGINT)

    def on_refresh_timer(self):
        if self.process is None:
            self.update_devices()

    def update_devices(self):
        prev = []
        for x in range(self.cmb_devices.count()):
            prev.append(self.cmb_devices.itemText(x))

        new = ["-"]

        usbdevs = usb.core.find(find_all=True)
        vidpid = set()
        for d in usbdevs:
            vidpid.add((d.idVendor, d.idProduct))

        for dev in DEVICES:
            if (dev.vid, dev.pid) in vidpid:
                new.append(dev.name)

        if new != prev:
            self.cmb_devices.clear()
            self.cmb_devices.addItems(new)

    def update_payloads(self):
        self.cmb_payloads.clear()
        self.cmb_payloads.addItem("-")
        current = self.cmb_devices.currentText()
        for dev in DEVICES:
            if dev.name == current:
                for payload in dev.commands.keys():
                    self.cmb_payloads.addItem(payload)


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
