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

    raise RuntimeError("Could not locate {} in supported devices list".format(args.phone))


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
        usage()
    else:
        main()
