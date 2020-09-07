# SPDX-License-Identifier: GPL-2.0-only
"""
arfile - A module to parse GNU ar archives.

Copyright (c) 2006-7 Paul Sokolovsky
This file is released under the terms 
of GNU General Public License v2 or later.
"""
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import tarfile 


class FileSection(object):
    "A class which allows to treat portion of file as separate file object."

    def __init__(self, f, offset, size):
        self.f = f
        self.offset = offset
        self.size = size
        self.seek(0, 0)

    def seek(self, offset, whence = 0):
#        print("seek(%x, %d)" % (offset, whence))
        if whence == 0:
            return self.f.seek(offset + self.offset, whence)
        elif whence == 1:
            return self.f.seek(offset, whence)
        elif whence == 2:
            return self.f.seek(self.offset + self.size + offset, 0)
        else:
            assert False

    def seekable(self):
        return True 

    def tell(self):
#        print("tell()")
        return self.f.tell() - self.offset

    def read(self, size = -1):
#        print("read(%d)" % size)
        return self.f.read(size)

class ArFile(object):

    def __init__(self, f, fn):
        self.f = f
        self.directory = {}
        self.directoryRead = False

        signature = self.f.readline()
        assert signature == "!<arch>\n" or signature == b"!<arch>\n", "Old ipk format (non-deb) is unsupported, file: %s, magic: %s, expected %s" % (fn, signature, "!<arch>")
        self.directoryOffset = self.f.tell()

    def open(self, fname):
        if fname in self.directory:
            return FileSection(self.f, self.directory[fname][-1], int(self.directory[fname][5]))

        if self.directoryRead:
            raise IOError("AR member not found: " + fname)

        f = self._scan(fname)
        if f == None:
            raise IOError("AR member not found: " + fname)
        return f


    def _scan(self, fname):
        self.f.seek(self.directoryOffset, 0)

        while True:
            l = self.f.readline()
            if not l: 
                self.directoryRead = True
                return None

            if l.decode('ascii') == "\n":
                l = self.f.readline()
                if not l: break
            l = l.decode('ascii')
            l = l.replace('`', '')
            # Field lengths from /usr/include/ar.h:
            ar_field_lens = [ 16, 12, 6, 6, 8, 10, 2 ]
            descriptor = []
            for field_len in ar_field_lens:
                descriptor.append(l[:field_len].strip())
                l = l[field_len:]
#            print(descriptor)
            size = int(descriptor[5])
            # Check for optional / terminator
            if descriptor[0][-1] == "/":
              memberName = descriptor[0][:-1]
            else:
              memberName = descriptor[0]
            self.directory[memberName] = descriptor + [self.f.tell()]
#            print(("read:", memberName))
            if memberName == fname:
                # Record directory offset to start from next time
                self.directoryOffset = self.f.tell() + size
                return FileSection(self.f, self.f.tell(), size)

            # Skip data and loop
            if size % 2:
                size = size + 1
            data = self.f.seek(size, 1)
#            print(hex(self.f.tell()))


if __name__ == "__main__":
    if None:
        fn = sys.argv[1]
        f = open(fn, "rb")

        ar = ArFile(f, fn)
        tarStream = ar.open("data.tar.gz")
        print("--------")
        tarStream = ar.open("data.tar.gz")
        print("--------")
        tarStream = ar.open("control.tar.gz")
        print("--------")
        tarStream = ar.open("control.tar.gz2")

        sys.exit(0)


    dir = "."
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    for f in os.listdir(dir):
        if not f.endswith(".opk") and not f.endswith(".ipk"): continue

        print("=== %s ===" % f)
        fn = "%s/%s" % (dir, f)
        f = open(fn, "rb")

        ar = ArFile(f, fn)
        tarStream = ar.open("control.tar.gz")
        tarf = tarfile.open("control.tar.gz", "r", tarStream)
        #tarf.list()

        try:
            f2 = tarf.extractfile("control")
        except KeyError:
            f2 = tarf.extractfile("./control")
        print(f2.read())
