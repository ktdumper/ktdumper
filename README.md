# `ktdumper`

`ktdumper` is a tool to dump memory contents of Japanese feature phones.

## Dependencies

On Ubuntu you can install the dependencies with:

```
sudo apt install gcc-arm-none-eabi
pip install -r requirements.txt
```

## Usage

Run `./ktdumper.sh` to show the list of supported devices. Afterwards, run the script with two arguments being the name of the device and the payload to execute. You may need to use "sudo" so that the script can access all USB devices. For example:

```
sudo ./ktdumper.sh p321ab dump_nor
sudo ./ktdumper.sh p321ab dump_nand
```

## Supported Devices
See the list here: https://ktdumper.github.io/ktdumper/
