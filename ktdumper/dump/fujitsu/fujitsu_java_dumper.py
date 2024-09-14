import tqdm
import string

from dump.fujitsu.fujitsu_protocol import FujitsuProtocol

PRINTABLE = string.printable.encode("ascii")

FIXED_PATHS = [
    "appicon",
    "Fulljar",
    "jam",
    "mainmaskmbm",
    "mainmbm",
    "maskmbm",
    "mbm",
    "Minijar",
    "sdf",
    "jar",
    "icon",
]
for x in range(32):
    FIXED_PATHS.append("sp{}".format(x))

class FujitsuJavaDumper(FujitsuProtocol):

    def find_jar_paths_in_db(self, db):
        paths = []
        idx = 0
        while True:
            idx = db.find(b".jar", idx)
            if idx == -1:
                break
            chunk = db[idx-256:idx+4]
            slash = chunk.rfind(b"\\")
            if slash != -1:
                chunk = chunk[slash+1:]
                good = True
                for ch in chunk:
                    if ch not in PRINTABLE:
                        good = False
                        break
                if good:
                    paths.append(chunk.decode("ascii"))

            idx += 1

        return paths

    def try_retrieve_file(self, rel_path):
        device_path = "D:\\WcdmaMp\\Java\\" + rel_path.replace("/", "\\")
        file_data = self.retrieve_file(device_path)
        if file_data is not None:
            with self.output.mkfile(rel_path) as outf:
                outf.write(file_data)

    def execute(self, dev, output):
        super().execute(dev, output)

        valid_idx = []

        print("Retrieving the database")
        db = self.retrieve_file("D:\\WcdmaMp\\Java\\FJJAM.DB")
        assert db is not None

        extra_jarpaths = self.find_jar_paths_in_db(db)

        print("Locating valid paths...")
        for x in tqdm.tqdm(range(300)):
            if self.retrieve_file("D:\\WcdmaMp\\Java\\Data\\{:02}\\jam".format(x)) is not None:
                valid_idx.append(x)

        print("Retrieving file data...")
        all_paths = ["FJJAM.DB", "JAMHIST.DB", "JAMREUSEENTRYID.DB",
            "SettingTrace", "WvControlData", "Bak/WvControlData"]

        for x in valid_idx:
            for sub in FIXED_PATHS + extra_jarpaths:
                all_paths.append("Data/{:02}/{}".format(x, sub))
                all_paths.append("Bak/{:02}/{}".format(x, sub))

        for path in tqdm.tqdm(all_paths):
            self.try_retrieve_file(path)
