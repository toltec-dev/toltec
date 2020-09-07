#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
#   Copyright (C) 2001 Alexander S. Guy <a7r@andern.org>
#                      Andern Research Labs
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330,
#   Boston, MA 02111-1307, USA.  */
#
#   Copyright 2001, Russell Nelson <opkg.py@russnelson.com>
#   Added reading in of packages.
#   Added missing package information fields.
#   Changed render_control() to __repr__().
#
# Current Issues:
#    The API doesn't validate package information fields.  It should be
#        throwing exceptions in the right places.
#    Executions of tar could silently fail.
#    Executions of tar *do* fail, and loudly, because you have to specify a full filename,
#        and tar complains if any files are missing, and the opkg spec doesn't require
#        people to say "./control.tar.gz" or "./control" when they package files.
#        It would be much better to require ./control or disallow ./control (either)
#        rather than letting people pick.  Some freedoms aren't worth their cost.
from __future__ import absolute_import
from __future__ import print_function

import tempfile
import os
import sys
import glob
import hashlib
import re
import subprocess
from stat import ST_SIZE
import arfile
import tarfile
import textwrap
import collections


def order(x):
    if not x:
        return 0
    if x == "~":
        return -1
    if str.isdigit(x):
        return 0
    if str.isalpha(x):
        return ord(x)

    return 256 + ord(x)


class Version(object):
    """A class for holding parsed package version information."""
    def __init__(self, epoch, version):
        self.epoch = epoch
        self.version = version

    def _versioncompare(self, selfversion, refversion):
        """
                Implementation below is a copy of the opkg version comparison algorithm
                http://git.yoctoproject.org/cgit/cgit.cgi/opkg/tree/libopkg/pkg.c*n933
                it alternates between number and non number comparisons until a difference is found
                digits are compared by value. other characters are sorted lexically using the above method orderOfChar

                One slight modification, the original version can return any value, whereas this one is limited to -1, 0, +1
                """
        if not selfversion: selfversion = ""
        if not refversion: refversion = ""

        value = list(selfversion)
        ref = list(refversion)

        while value or ref:
            first_diff = 0
            # alphanumeric comparison
            while (value and not str.isdigit(value[0])) or (ref and not str.isdigit(ref[0])):
                vc = order(value.pop(0) if value else None)
                rc = order(ref.pop(0) if ref else None)
                if vc != rc:
                    return -1 if vc < rc else 1

            # comparing numbers
            # start by skipping 0
            while value and value[0] == "0":
                value.pop(0)
            while ref and ref[0] == "0":
                ref.pop(0)

            # actual number comparison
            while value and str.isdigit(value[0]) and ref and str.isdigit(ref[0]):
                if not first_diff:
                    first_diff = int(value.pop(0)) - int(ref.pop(0))
                else:
                    value.pop(0)
                    ref.pop(0)

            # the one that has a value remaining was the highest number
            if value and str.isdigit(value[0]):
                return 1
            if ref and str.isdigit(ref[0]):
                return -1
            # in case of equal length numbers look at the first diff
            if first_diff:
                return 1 if first_diff > 0 else -1
        return 0

    def compare(self, ref):
        if (self.epoch > ref.epoch):
            return 1
        elif (self.epoch < ref.epoch):
            return -1
        else:
            self_ver_comps = re.match(r"(.+?)(-r.+)?$", self.version)
            ref_ver_comps = re.match(r"(.+?)(-r.+)?$", ref.version)
            #print((self_ver_comps.group(1), self_ver_comps.group(2)))
            #print((ref_ver_comps.group(1), ref_ver_comps.group(2)))
            r = self._versioncompare(self_ver_comps.group(1), ref_ver_comps.group(1))
            if r == 0:
                r = self._versioncompare(self_ver_comps.group(2), ref_ver_comps.group(2))
            #print("compare: %s vs %s = %d" % (self, ref, r))
            return r

    def __str__(self):
        return str(self.epoch) + ":" + self.version

def parse_version(versionstr):
    epoch = 0
    # check for epoch
    m = re.match('([0-9]*):(.*)', versionstr)
    if m:
        (epochstr, versionstr) = m.groups()
        epoch = int(epochstr)
    return Version(epoch, versionstr)

class Package(object):
    """A class for creating objects to manipulate (e.g. create) opkg
       packages."""

    # fn: Package file path
    # relpath: If this argument is set, the file path is given relative to this
    #   path when a string representation of the Package object is created. If
    #   this argument is not set, the basename of the file path is given.
    def __init__(self, fn=None, relpath=None, all_fields=None):
        self.package = None
        self.version = 'none'
        self.parsed_version = None
        self.architecture = None
        self.maintainer = None
        self.source = None
        self.description = None
        self.depends = None
        self.provides = None
        self.replaces = None
        self.conflicts = None
        self.recommends = None
        self.suggests = None
        self.section = None
        self.filename_header = None
        self.file_list = []
        # md5 and size is lazy attribute, computed on demand
        #self.md5 = None
        #self.size = None
        self.installed_size = None
        self.filename = None
        self.file_ext_opk = "ipk"
        self.homepage = None
        self.oe = None
        self.priority = None
        self.tags = None
        self.fn = fn
        self.license = None

        self.user_defined_fields = collections.OrderedDict()
        if fn:
            # see if it is deb format
            f = open(fn, "rb")

            if relpath:
                self.filename = os.path.relpath(fn, relpath)
            else:
                self.filename = os.path.basename(fn)

            ## sys.stderr.write("  extracting control.tar.gz from %s\n"% (fn,)) 

            if tarfile.is_tarfile(fn):
                tar = tarfile.open(fn, "r", f)
                tarStream = tar.extractfile("./control.tar.gz")
            else:
                ar = arfile.ArFile(f, fn)
                tarStream = ar.open("control.tar.gz")
            tarf = tarfile.open("control.tar.gz", "r", tarStream)
            try:
                control = tarf.extractfile("control")
            except KeyError:
                control = tarf.extractfile("./control")
            try:
                self.read_control(control, all_fields)
            except TypeError as e:
                sys.stderr.write("Cannot read control file '%s' - %s\n" % (fn, e))
            control.close()
        self.scratch_dir = None
        self.file_dir = None
        self.meta_dir = None

    def __getattr__(self, name):
        if name == "md5":
            self._computeFileMD5()
            return self.md5
        elif name == "sha256":
            self._computeFileSHA256()
            return self.sha256
        elif name == 'size':
            return self._get_file_size()
        else:
            raise AttributeError(name)

    def _computeFileMD5(self):
        # compute the MD5.
        if not self.fn:
            self.md5 = 'Unknown'
        else:
            f = open(self.fn, "rb")
            sum = hashlib.md5()
            while True:
               data = f.read(1024)
               if not data: break
               sum.update(data)
            f.close()
            self.md5 = sum.hexdigest()

    def _computeFileSHA256(self):
        # compute the SHA256.
        if not self.fn:
            self.sha256 = 'Unknown'
        else:
            f = open(self.fn, "rb")
            sum = hashlib.sha256()
            while True:
               data = f.read(1024)
               if not data: break
               sum.update(data)
            f.close()
            self.sha256 = sum.hexdigest()

    def _get_file_size(self):
        if not self.fn:
            self.size = 0;
        else:
            stat = os.stat(self.fn)
            self.size = stat[ST_SIZE]
        return int(self.size)

    def read_control(self, control, all_fields=None):
        import os

        line = control.readline()
        while 1:
            if not line: break
            # Decode if stream has byte strings
            if not isinstance(line, str):
                line = line.decode()
            line = line.rstrip()
            lineparts = re.match(r'([\w-]*?):\s*(.*)', line)
            if lineparts:
                name = lineparts.group(1)
                name_lowercase = name.lower()
                value = lineparts.group(2)
                while 1:
                    line = control.readline().rstrip()
                    if not line: break
                    if line[0] != ' ': break
                    value = value + '\n' + line
                if name_lowercase == 'size':
                    self.size = int(value)
                elif name_lowercase == 'md5sum':
                    self.md5 = value
                elif name_lowercase == 'sha256sum':
                    self.sha256 = value
                elif name_lowercase in self.__dict__:
                    self.__dict__[name_lowercase] = value
                elif all_fields:
                    self.user_defined_fields[name] = value
                else:
                    print("Lost field %s, %s" % (name,value))
                    pass

                if line and line[0] == '\n':
                    return # consumes one blank line at end of package descriptoin
            else:
                line = control.readline()
                pass
        return    

    def _setup_scratch_area(self):
        self.scratch_dir = "%s/%sopkg" % (tempfile.gettempdir(),
                                           tempfile.gettempprefix())
        self.file_dir = "%s/files" % (self.scratch_dir)
        self.meta_dir = "%s/meta" % (self.scratch_dir)

        os.mkdir(self.scratch_dir)
        os.mkdir(self.file_dir)
        os.mkdir(self.meta_dir)

    def set_package(self, package):
        self.package = package

    def get_package(self):
        return self.package

    def set_version(self, version):
        self.version = version
        self.parsed_version = parse_version(version)

    def get_version(self):
        return self.version

    def set_architecture(self, architecture):
        self.architecture = architecture

    def get_architecture(self):
        return self.architecture

    def set_maintainer(self, maintainer):
        self.maintainer = maintainer

    def get_maintainer(self):
        return self.maintainer

    def set_source(self, source):
        self.source = source

    def get_source(self):
        return self.source

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_depends(self, depends):
        self.depends = depends

    def get_depends(self, depends):
        return self.depends

    def set_provides(self, provides):
        self.provides = provides

    def get_provides(self, provides):
        return self.provides

    def set_replaces(self, replaces):
        self.replaces = replaces

    def get_replaces(self, replaces):
        return self.replaces

    def set_conflicts(self, conflicts):
        self.conflicts = conflicts

    def get_conflicts(self, conflicts):
        return self.conflicts

    def set_suggests(self, suggests):
        self.suggests = suggests

    def get_suggests(self, suggests):
        return self.suggests

    def set_section(self, section):
        self.section = section

    def get_section(self, section):
        return self.section

    def set_license(self, license):
        self.license = license

    def get_license(self, license):
        return self.license

    def get_file_list_dir(self, directory):
        def check_output(*popenargs, **kwargs):
            """Run command with arguments and return its output as a byte string.

            Backported from Python 2.7 as it's implemented as pure python on stdlib.

            >>> check_output(['/usr/bin/python', '--version'])
            Python 2.6.2
            """
            process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
            output, unused_err = process.communicate()
            retcode = process.poll()
            if retcode:
                cmd = kwargs.get("args")
                if cmd is None:
                    cmd = popenargs[0]
                error = subprocess.CalledProcessError(retcode, cmd)
                error.output = output
                raise error
            output = output.decode("utf-8")
            return output

        if not self.fn:
            try:
                cmd = "find %s -name %s | head -n 1" % (directory, self.filename)
                rc = check_output(cmd, shell=True)
                if rc != "":
                    newfn = str(rc).split()[0]
#                    sys.stderr.write("Package '%s' with empty fn and filename is '%s' was found in '%s', updating fn\n" % (self.package, self.filename, newfn))
                    self.fn = newfn
            except OSError as e:
                sys.stderr.write("Cannot find current fn for package '%s' filename '%s' in dir '%s'\n(%s)\n" % (self.package, self.filename, directory, e))
            except IOError as e:
                sys.stderr.write("Cannot find current fn for package '%s' filename '%s' in dir '%s'\n(%s)\n" % (self.package, self.filename, directory, e))
        return self.get_file_list()


    def get_file_list(self):
        if not self.fn:
            sys.stderr.write("Package '%s' has empty fn, returning empty filelist\n" % (self.package))
            return []
        f = open(self.fn, "rb")
        ar = arfile.ArFile(f, self.fn)
        try:
            tarStream = ar.open("data.tar.gz")
            tarf = tarfile.open("data.tar.gz", "r", tarStream)
        except IOError:
            tarStream = ar.open("data.tar.xz")
            tarf = tarfile.open("data.tar.xz", "r:xz", tarStream)
        self.file_list = tarf.getnames()
        self.file_list = [["./", ""][a.startswith("./")] + a for a in self.file_list]

        f.close()
        return self.file_list

    def set_package_extension(self, ext="ipk"):
        self.file_ext_opk = ext

    def get_package_extension(self):
        return self.file_ext_opk

    def write_package(self, dirname):
        self._setup_scratch_area()
        file = open("%s/control" % self.meta_dir, 'w')
        file.write(str(self))
        file.close()

        cmd = "cd %s ; tar cvz --format=gnu -f %s/control.tar.gz control" % (self.meta_dir,
                                                              self.scratch_dir)

        cmd_out, cmd_in, cmd_err = os.popen3(cmd)
        
        while cmd_err.readline() != "":
            pass

        cmd_out.close()
        cmd_in.close()
        cmd_err.close()

        bits = "control.tar.gz"

        if self.file_list:
                cmd = "cd %s ; tar cvz --format=gnu -f %s/data.tar.gz" % (self.file_dir,
                                                              self.scratch_dir)

                cmd_out, cmd_in, cmd_err = os.popen3(cmd)

                while cmd_err.readline() != "":
                    pass

                cmd_out.close()
                cmd_in.close()
                cmd_err.close()

                bits = bits + " data.tar.gz"

        file = "%s_%s_%s.%s" % (self.package, self.version, self.architecture, self.get_package_extension())
        cmd = "cd %s ; tar cvz --format=gnu -f %s/%s %s" % (self.scratch_dir,
                                             dirname,
                                             file,
                                             bits)

        cmd_out, cmd_in, cmd_err = os.popen3(cmd)

        while cmd_err.readline() != "":
            pass

        cmd_out.close()
        cmd_in.close()
        cmd_err.close()

    def compare_version(self, ref):
        """Compare package versions of self and ref"""
        if not self.version:
            print('No version for package %s' % self.package)
        if not ref.version:
            print('No version for package %s' % ref.package)
        if not self.parsed_version:
            self.parsed_version = parse_version(self.version)
        if not ref.parsed_version:
            ref.parsed_version = parse_version(ref.version)
        return self.parsed_version.compare(ref.parsed_version)

    def print(self, checksum):
        out = ""

        # XXX - Some checks need to be made, and some exceptions
        #       need to be thrown. -- a7r

        if self.package: out = out + "Package: %s\n" % (self.package)
        if self.version: out = out + "Version: %s\n" % (self.version)
        if self.depends: out = out + "Depends: %s\n" % (self.depends)
        if self.provides: out = out + "Provides: %s\n" % (self.provides)
        if self.replaces: out = out + "Replaces: %s\n" % (self.replaces)
        if self.conflicts: out = out + "Conflicts: %s\n" % (self.conflicts)
        if self.suggests: out = out + "Suggests: %s\n" % (self.suggests)
        if self.recommends: out = out + "Recommends: %s\n" % (self.recommends)
        if self.section: out = out + "Section: %s\n" % (self.section)
        if self.architecture: out = out + "Architecture: %s\n" % (self.architecture)
        if self.maintainer: out = out + "Maintainer: %s\n" % (self.maintainer)
        if 'md5' in checksum:
            if self.md5: out = out + "MD5Sum: %s\n" % (self.md5)
        if 'sha256' in checksum:
            if self.sha256: out = out + "SHA256sum: %s\n" % (self.sha256)
        if self.size: out = out + "Size: %d\n" % int(self.size)
        if self.installed_size: out = out + "InstalledSize: %d\n" % int(self.installed_size)
        if self.filename: out = out + "Filename: %s\n" % (self.filename)
        if self.source: out = out + "Source: %s\n" % (self.source)
        if self.description: out = out + "Description: %s\n" % (self.description)
        if self.oe: out = out + "OE: %s\n" % (self.oe)
        if self.homepage: out = out + "HomePage: %s\n" % (self.homepage)
        if self.license: out = out + "License: %s\n" % (self.license)
        if self.priority: out = out + "Priority: %s\n" % (self.priority)
        if self.tags: out = out + "Tags: %s\n" % (self.tags)
        if self.user_defined_fields:
            for k, v in self.user_defined_fields.items():
                out = out + "%s: %s\n" % (k, v)
        out = out + "\n"

        return out

    def __del__(self):
        # XXX - Why is the `os' module being yanked out before Package objects
        #       are being destroyed?  -- a7r
        pass

class Packages(object):
    """A currently unimplemented wrapper around the opkg utility."""
    def __init__(self):
        self.packages = {}
        return

    def add_package(self, pkg, opt_a=0):
        package = pkg.package
        arch = pkg.architecture
        ver = pkg.version
        if opt_a:
            name = ("%s:%s:%s" % (package, arch, ver))
        else:
            name = ("%s:%s" % (package, arch))

        if (name not in self.packages):
            self.packages[name] = pkg
        
        if pkg.compare_version(self.packages[name]) >= 0:
            self.packages[name] = pkg
            return 0
        else:
            return 1

    def read_packages_file(self, fn, all_fields=None):
        f = open(fn, "r")
        while True:
            pkg = Package()
            try:
                pkg.read_control(f, all_fields)
            except TypeError as e:
                sys.stderr.write("Cannot read control file '%s' - %s\n" % (fn, e))
                continue
            if pkg.get_package():
                self.add_package(pkg)
            else:
                break
        f.close()    
        return

    def write_packages_file(self, fn):
        f = open(fn, "w")
        names = list(self.packages.keys())
        names.sort()
        for name in names:
            f.write(self.packages[name].__str__())
        return    

    def keys(self):
        return list(self.packages.keys())

    def __getitem__(self, key):
        return self.packages[key]

if __name__ == "__main__":

    assert Version(0, "1.2.2-r1").compare(Version(0, "1.2.3-r0")) == -1
    assert Version(0, "1.2.2-r0").compare(Version(0, "1.2.2+cvs20070308-r0")) == -1
    assert Version(0, "1.2.2+cvs20070308").compare(Version(0, "1.2.2-r0")) == 1
    assert Version(0, "1.2.2-r0").compare(Version(0, "1.2.2-r0")) == 0
    assert Version(0, "1.2.2-r5").compare(Version(0, "1.2.2-r0")) == 1
    assert Version(0, "1.1.2~r1").compare(Version(0, "1.1.2")) == -1

    package = Package()

    package.set_package("FooBar")
    package.set_version("0.1-fam1")
    package.set_architecture("arm")
    package.set_maintainer("Testing <testing@testing.testing>")
    package.set_depends("libc")
    package.set_description("A test of the APIs. And very long descriptions so often used in oe-core\nfoo\n\n\nbar")

    print("<")
    sys.stdout.write(str(package))
    print(">")
    f = open("/tmp/control", "w")
    f.write(str(package))
    f.close()

    f = open("/tmp/control", "r")
    package2 = Package()
    package2.read_control(f)
    print("<")
    sys.stdout.write(str(package2))
    print(">")

    package.write_package("/tmp")

