import tqdm
from pathlib import Path, PureWindowsPath
import random

from dump.fujitsu.fujitsu_protocol import FujitsuProtocol


class FujitsuFsDumper(FujitsuProtocol):
    def try_retrieve_file(self, path):
        file_data = self.retrieve_file(path)
        if file_data is not None:
            symbian_path = PureWindowsPath(path)
            rel = symbian_path.relative_to(symbian_path.anchor)
            with self.output.mkfile(rel.as_posix()) as outf:
                outf.write(file_data)

    def execute(self, dev, output):
        super().execute(dev, output)

        print("Retrieving the file list...")
        file_paths = self.get_file_paths_deep("D:\\")
        # To slightly reduce uneven progress in the progress bar.
        random.shuffle(file_paths)

        print("Retrieving file data...")
        for path in tqdm.tqdm(file_paths):
            self.try_retrieve_file(path)
