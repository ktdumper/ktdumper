import usb.core
import datetime
import os

from util.output_manager import OutputManager


class Device:

    def __init__(self, name, target, commands, **kwargs):
        if isinstance(target, tuple):
            self.vid, self.pid = target
            self.target = "usb"
        else:
            self.target = target
        self.name = name
        self.commands = commands
        self.device_opts = kwargs

    def execute(self, args):
        if args.module in self.commands:
            dumper = self.commands[args.module]

            if self.target == "usb":
                dumper.target_vid, dumper.target_pid = self.vid, self.pid
                dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
                if dev is None and self.device_opts.get("help"):
                    print("!" * 80)
                    print(self.device_opts["help"])
                    print("!" * 80)
                    return
                if dev is None and not self.device_opts.get("allow_no_device") and not dumper.dumper_opts.get("allow_no_device"):
                    raise RuntimeError("Cannot find '{}' (vid=0x{:04X} pid=0x{:04X}), is the phone connected?".format(self.name, self.vid, self.pid))
            elif self.target == "serial":
                dev = args.serial
                if dev is None:
                    raise RuntimeError("specify an additional `--serial /dev/ttyUSB123` or `--serial /dev/ttyACM321` argument to dump this device")
                if not os.path.exists(dev):
                    raise RuntimeError(f"specified serial device {dev} does not exist")
            else:
                raise RuntimeError(f"device has unknown target {self.target}")

            directory = "KTdumper_{}_{}_{}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), self.name, args.module)
            output = OutputManager(directory, args.module)
            dumper.set_device_opts(self.device_opts)
            dumper.execute(dev, output)
        else:
            raise RuntimeError("Unsupported command for '{}': '{}'".format(self.name, args.module))
