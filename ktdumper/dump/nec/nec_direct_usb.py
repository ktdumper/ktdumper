from dump.nec.nec_protocol import NecProtocol
from util.payload_builder import PayloadBuilder


class NecDirectUsb(NecProtocol):

    """ This payload will access USB functions directly by calling firmware functions
    rather than going through memory read commands """

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.usb_command = opts["usb_command"]
        self.usb_data = opts["usb_data"]
        self.usb_datasz = opts["usb_datasz"]
        self.usb_respfunc = opts["usb_respfunc"]
        self.payload_base = opts["payload_base"]

    def builder_opts(self):
        return dict(
            base=self.payload_base,
            usb_command=self.usb_command,
            usb_data=self.usb_data,
            usb_datasz=self.usb_datasz,
            usb_respfunc=self.usb_respfunc,
            patch=self.patch,
            keep_mmu=self.keep_mmu,
        )

    def insert_payload(self, name, **kwargs):
        opts = self.builder_opts().copy()
        opts.update(kwargs)
        payload = PayloadBuilder(name).build(**opts)
        self.cmd_write(self.payload_base, payload)

        # must execute one no-op first to trigger the smc cleanup code
        if self.patch:
            self.cmd_exec()
