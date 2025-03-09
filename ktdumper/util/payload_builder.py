import os.path
import tempfile
import subprocess


PAYLOAD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "payload")
LINKER = """
ENTRY(start)

SECTIONS
{
  . = BASE;

  .text     : { *(.text.start) *(.text   .text.*   .gnu.linkonce.t.*) }
  .rodata   : { *(.rodata .rodata.* .gnu.linkonce.r.*) }
  .bss      : { *(.bss    .bss.*    .gnu.linkonce.b.*) *(COMMON) }
  .data     : { *(.data   .data.*   .gnu.linkonce.d.*) }
  /DISCARD/ : { *(.interp) *(.dynsym) *(.dynstr) *(.hash) *(.dynamic) *(.comment) }
}
"""

COMPILE = ["arm-none-eabi-gcc", "-c", "-Os", "-march=armv4", "-ffixed-r4", "-ffixed-r5", "-fno-builtin-printf", "-fno-strict-aliasing", "-fno-builtin-memcpy", "-fno-builtin-memset", "-fno-builtin",
    "-I", PAYLOAD_PATH]
LINK = ["arm-none-eabi-gcc", "-nodefaultlibs", "-nostdlib"]
OBJCOPY = ["arm-none-eabi-objcopy", "-O", "binary"]


class PayloadBuilder:

    def __init__(self, srcfile):
        with open(os.path.join(PAYLOAD_PATH, srcfile)) as inf:
            self.src = inf.read()

    def build(self, **kwargs):
        base = kwargs["base"]
        src = self.src

        defs = []
        for arg, replacement in kwargs.items():
            src = src.replace("%{}%".format(arg), str(replacement))
            defs += ["-DKT_{}={}".format(arg, str(replacement))]

        with tempfile.TemporaryDirectory() as tmp:
            p_linker_x = os.path.join(tmp, "linker.x")
            p_payload_c = os.path.join(tmp, "payload.c")
            p_payload_o = os.path.join(tmp, "payload.o")
            p_payload = os.path.join(tmp, "payload")
            p_payload_bin = os.path.join(tmp, "payload.bin")

            with open(p_linker_x, "w") as outf:
                outf.write(LINKER.replace("BASE", hex(base)))
            with open(p_payload_c, "w") as outf:
                outf.write(src)
            subprocess.check_output(COMPILE + defs + ["-o", p_payload_o, p_payload_c])
            subprocess.check_output(LINK + ["-T", p_linker_x, "-o", p_payload, p_payload_o])
            subprocess.check_output(OBJCOPY + [p_payload, p_payload_bin])
            with open(p_payload_bin, "rb") as inf:
                payload = inf.read()
        while len(payload) % 4 != 0:
            payload += b"\x00"
        payload += b"\x00" * 0x100
        return payload
