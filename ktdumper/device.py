import usb.core
import datetime

from util.output_manager import OutputManager


class Device:

    def __init__(self, name, vid, pid, commands, **kwargs):
        self.name = name
        self.vid = vid
        self.pid = pid
        self.commands = commands
        self.device_opts = kwargs

    def execute(self, args):
        if args.module in self.commands:
            dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
            if dev is None:
                raise RuntimeError("Cannot find '{}' (vid=0x{:04X} pid=0x{:04X}), is the phone connected?".format(self.name, self.vid, self.pid))
            directory = "KTdumper_{}_{}_{}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), self.name, args.module)
            output = OutputManager(directory)
            print("Writing output to {}".format(directory))
            dumper = self.commands[args.module]
            dumper.set_device_opts(self.device_opts)
            dumper.execute(dev, output)
        else:
            raise RuntimeError("Unsupported command for '{}': '{}'".format(self.name, args.module))
