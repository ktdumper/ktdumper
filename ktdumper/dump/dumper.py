class Dumper:

    def __init__(self, **kwargs):
        self.dumper_opts = kwargs

    def parse_opts(self, opts):
        pass

    def set_device_opts(self, device_opts):
        self.device_opts = device_opts
        self.opts = device_opts.copy()
        self.opts.update(self.dumper_opts)

        self.parse_opts(self.opts)
