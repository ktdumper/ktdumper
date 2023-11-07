import pathlib
import os.path


class OutputManager:

    def __init__(self, directory):
        if os.path.exists(directory):
            raise RuntimeError("Directory {} already exists, please move it out of the way".format(directory))
        self.directory = directory

    def mkfile(self, name):
        pathlib.Path(self.directory).mkdir(parents=True, exist_ok=True)
        return open(os.path.join(self.directory, name), "wb")
