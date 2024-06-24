import sys
import argparse

from devices import DEVICES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phone")
    parser.add_argument("module")
    args = parser.parse_args()

    for dev in DEVICES:
        if dev.name == args.phone:
            return dev.execute(args)

    usage()
    print("")
    raise RuntimeError(
        "Could not locate {} in supported devices list".format(args.phone))


def supported_devices():
    print('[', end="")
    first = True
    for dev in DEVICES:
        if not first:
            print(',', end="")

        print('{', end="")
        print('"name": "{}",'.format(dev.name), end="")
        print('"vid": "{:04x}",'.format(dev.vid), end="")
        print('"pid": "{:04x}",'.format(dev.pid), end="")
        print('"commands": [', end="")
        first_command = True
        for cmd in sorted(dev.commands.keys()):
            if not first_command:
                print(',', end="")

            print('"{}"'.format(cmd), end="")

            first_command = False
        print(']', end="")
        print('}', end="")

        first = False
    print(']', "\n")


def usage():
    print("Usage: ./ktdumper.sh <device> <payload>")
    print("")
    print("List of supported devices and payloads:")
    for dev in DEVICES:
        s = "- {}: ".format(dev.name)
        s += ", ".join(sorted(dev.commands.keys()))
        print(s)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        if sys.argv[1] == "--supported":
            supported_devices()
        else:
            usage()
    else:
        main()
