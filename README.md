# `ktdumper`

`ktdumper` is a tool to dump memory contents of Japanese feature phones.

## Dependencies

On Ubuntu you can install the dependencies with:

```
sudo apt install python3-usb python3-tqdm gcc-arm-none-eabi python3-fusepy
```

## Usage

Run `./ktdumper.sh` to show the list of supported devices. Afterwards, run the script with two arguments being the name of the device and the payload to execute. You may need to use "sudo" so that the script can access all USB devices. For example:

```
sudo ./ktdumper.sh p321ab dump_nor
sudo ./ktdumper.sh p321ab dump_nand
```

## Notes

For DoCoMo devices (and Softbank phones from Panasonic/NEC/Casio), you must remove the battery before plugging in the phone to use ktdumper.

Make sure to unplug and replug the phone after each command.
