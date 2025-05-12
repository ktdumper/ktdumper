import tqdm
import string
import os

from dump.fujitsu.fujitsu_protocol import FujitsuProtocol

PRINTABLE = string.printable.encode("ascii")

FIXED_PATHS = list(map(lambda x : "sp{}".format(x), range(16)))

class FujitsuJavaDumperAlternative(FujitsuProtocol):

    def find_jar_paths_in_db(self, db):
        paths = []
        idx = 0
        while True:
            idx = db.find(b".jar", idx)
            if idx == -1:
                break
            chunk = db[idx-256:idx+4]
            firstslash = chunk.rfind(b"\\")
            secondslash = chunk[:firstslash].rfind(b"\\")
            if secondslash != -1:
                chunk = chunk[secondslash+1:]
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
        device_path = rel_path.replace("/", "\\")  
        file_data = self.retrieve_file(device_path)

        if file_data is not None:
            linux_path = rel_path.replace("\\", "/").replace("D:/Sanremo", "").lstrip("/")
            with self.output.mkfile(linux_path) as outf:
                outf.write(file_data)


    def execute(self, dev, output):
        super().execute(dev, output)
        
        print("-" * 80)
        print("NOTE: This phone dump will require rebuilding of JAM files. No JAM files will be dumped using this method.")
        print("-" * 80)

        print("Retrieving the database")
        db = self.retrieve_file("D:\\Sanremo\\Java\\FJJAM.DB")
        assert db is not None

        applidirs = self.find_jar_paths_in_db(db)
        
        all_paths = ["D:\\Sanremo\\Java\\FJJAM.DB", "D:\\Sanremo\\Java\\JAMHIST.DB", "D:\\Sanremo\\Java\\JAMREUSEENTRYID.DB"]
        
        print("Creating valid directory list for all appli folders...")
        for x in range(len(applidirs)):
            folder_idx = applidirs[x][:2]
            base_name = applidirs[x][applidirs[x].find("\\")+1:applidirs[x].find(".")]
            folder_str = f"D:\\Sanremo\\Java\\{folder_idx}\\"
            all_paths.append(f"{folder_str}{base_name}.jam")
            all_paths.append(f"{folder_str}{base_name}.jar")
            for sub in FIXED_PATHS:
                all_paths.append(f"{folder_str}{sub}")
        
        for path in tqdm.tqdm(all_paths):
            self.try_retrieve_file(path)
