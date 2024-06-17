import os
import errno
import struct
import math

from dump.pipl_exploit import PiplExploit
from util.payload_builder import PayloadBuilder

from fusepy import FUSE, FuseOSError, Operations, fuse_get_context


PATH = "/tmp/ktdumper_fuse"


class EmmcMounter(Operations):

    def __init__(self, size, read_cb, write_cb):
        self.size = size
        self.read_cb = read_cb
        self.write_cb = write_cb

    def access(self, path, mode):
        return 0

    def open(self, path, flags):
        return 0

    def flush(self, path, fh):
        return 0

    def release(self, path, fh):
        return 0

    def fsync(self, path, fdatasync, fh):
        return 0

    def truncate(self, path, length, fh=None):
        raise FuseOSError(errno.EACCES)

    def create(self, path, mode, fi=None):
        raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        raise FuseOSError(errno.EACCES)

    def chown(self, path, uid, gid):
        raise FuseOSError(errno.EACCES)

    def readdir(self, path, fh):
        raise FuseOSError(errno.EACCES)

    def readlink(self, path):
        raise FuseOSError(errno.EACCES)

    def mknod(self, path, mode, dev):
        raise FuseOSError(errno.EACCES)

    def rmdir(self, path):
        raise FuseOSError(errno.EACCES)

    def mkdir(self, path, mode):
        raise FuseOSError(errno.EACCES)

    def unlink(self, path):
        raise FuseOSError(errno.EACCES)

    def symlink(self, name, target):
        raise FuseOSError(errno.EACCES)

    def rename(self, old, new):
        raise FuseOSError(errno.EACCES)

    def link(self, target, name):
        raise FuseOSError(errno.EACCES)

    def utimens(self, path, times=None):
        raise FuseOSError(errno.EACCES)

    def getattr(self, path, fh=None):
        return {
            "st_atime": 0,
            "st_ctime": 0,
            "st_mtime": 0,
            "st_gid": 0,
            "st_uid": 0,
            "st_mode": 0o100644,
            "st_nlink": 1,
            "st_size": self.size,
        }

    def statfs(self, path):
        return {
            "f_bsize": 4096,
            "f_frsize": 4096,
            "f_blocks": 1024,
            "f_bfree": 0,
            "f_bavail": 0,
            "f_files": 1,
            "f_ffree": 0,
            "f_fsid": 0,
            "f_favail": 0,
            "f_flag": 4096,
            "f_namemax": 255,
        }

    def read(self, path, length, offset, fh):
        if length % 512 != 0 or offset % 512 != 0:
            raise FuseOSError(errno.EINVAL)

        data = b""
        for blk in range(length // 512):
            data += self.read_cb(offset // 512 + blk)

        return data

    def write(self, path, buf, offset, fh):
        ret = 0
        if offset % 512 != 0 or len(buf) % 512 != 0:
            raise FuseOSError(errno.EINVAL)
        for blk in range(len(buf) // 512):
            ret += self.write_cb(offset // 512 + blk, buf[blk*512:(blk+1)*512])
        return ret


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s%s" % (s, size_name[i])


class PiplEmmcFuse(PiplExploit):

    progressbar = "\\|/"

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.size = opts["size"]
        self.offset = opts["offset"]
        assert self.offset % 512 == 0

        self.emmc_read_and_dcache = opts["emmc_read_and_dcache"]
        self.emmc_inv_dcache_and_write = opts["emmc_inv_dcache_and_write"]
        self.usb_command = opts["usb_command"]
        self.usb_data = opts["usb_data"]
        self.usb_datasz = opts["usb_datasz"]
        self.usb_respfunc = opts["usb_respfunc"]
        self.payload_base = opts["payload_base"]

    def unwrap_read(self, data, size):
        assert len(data) == size + 10
        return data[9:-1]

    def _emmc_read_page(self, page):
        self.comm(3, variable_payload=struct.pack("<BBI", 1, 0, page))
        return self.unwrap_read(self.read_resp(), 512)

    def _emmc_write_page(self, page, data):
        self.comm(3, variable_payload=struct.pack("<BBI", 1, 1, page) + data)
        self.unwrap_read(self.read_resp(), 0)

    def execute(self, dev, output):
        super().execute(dev, output)

        self.bytes_read = self.bytes_written = self.progress = 0

        payload = PayloadBuilder("emmc_rw.c").build(
            base=self.payload_base,
            emmc_read_and_dcache=self.emmc_read_and_dcache,
            emmc_inv_dcache_and_write=self.emmc_inv_dcache_and_write,
            usb_command=self.usb_command,
            usb_data=self.usb_data,
            usb_datasz=self.usb_datasz,
            usb_respfunc=self.usb_respfunc,
        )
        self.cmd_write(self.payload_base, payload)

        try:
            os.unlink(PATH)
        except FileNotFoundError:
            pass
        os.mknod(PATH)

        print("")
        print("Next, to mount the filesystem enter one of the two following:")
        print("- For read-only access:  `sudo mount -o loop,ro,noload {} /mnt`".format(PATH))
        print("- For read-write access: `sudo mount -o loop {} /mnt`".format(PATH))
        print("")
        print("Don't forget to unmount it with `sudo unmount /mnt` before terminating ktdumper!")
        print("")

        FUSE(EmmcMounter(self.size, self.read_cb, self.write_cb), PATH, nothreads=True, foreground=True, allow_other=True)

    def read_cb(self, idx):
        idx += self.offset // 512
        data = self._emmc_read_page(idx)

        self.bytes_read += 512
        self.print_stats()

        return data

    def print_stats(self):
        print("\r{} FUSE Running | Read {} | Wrote {}\033[K".format(self.progressbar[self.progress],
            convert_size(self.bytes_read), convert_size(self.bytes_written)), end="")
        self.progress = (self.progress + 1) % len(self.progressbar)

    def write_cb(self, idx, data):
        idx += self.offset // 512
        assert len(data) == 512

        self._emmc_write_page(idx, data)

        self.bytes_written += 512
        self.print_stats()

        return 512
