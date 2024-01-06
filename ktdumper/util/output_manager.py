import pathlib
import os.path


class OutputManager:

    def __init__(self, directory, prefix):
        if os.path.exists(directory):
            raise RuntimeError("Directory {} already exists, please move it out of the way".format(directory))
        self.directory = directory
        self.prefix = prefix

    def _ensure_output(self):
        pathlib.Path(self.directory).mkdir(parents=True, exist_ok=True)

    def mkfile(self, name):
        self._ensure_output()
        full_path = os.path.join(self.directory, name)
        pathlib.Path(full_path).parent.mkdir(parents=True, exist_ok=True)
        return open(full_path, "wb")

    def mksuff(self, suff):
        self._ensure_output()
        return open(os.path.join(self.directory, self.prefix + suff), "wb")
