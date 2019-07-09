#!/usr/bin/env python3
#
# rpm2mc.py -- Generate a Kubernetes machine-config from an RPM
# Copyright (c) 2019 Brian 'redbeard' Harrington <redbeard@dead-city.org>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import base64
import mimetypes
import os
import rpm
import sys
import yaml

from optparse import OptionParser

# Create the stub of a machine-config object to hold our resulting output
mco = {"spec": {"config": {
                        "storage": {"files": []},
                        "systemd": {"units": []}
                        }
               }
      }

class FileNotFoundError(Exception):
    """Class to simplify the handling of missing files"""
    pass

def file_to_data(path):
    """Convert a file (specified by a path) into a data URI."""
    if not os.path.exists(path):
        raise FileNotFoundError
    mime, _ = mimetypes.guess_type(path)
    data64 = base64.b64encode(open(path, "rb").read())
    return 'data:{};base64,{}'.format(mime, data64.decode('UTF-8'))

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="isFile",
                      action="store_true",
                      help="read data from FILENAME")
    parser.add_option("-a", "--all", action="store_true", dest="allFiles",
                      help="store all files, not just configs and systemd units")
    parser.add_option("-v", action="store_true", dest="verbose")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        print(len(args))
        parser.error("incorrect number of arguments")
        sys.exit(1)

    pkg = args[0]
    ts = rpm.TransactionSet()
    if options.isFile:
        fdno = os.open(pkg, os.O_RDONLY)
        try:
            hdr = ts.hdrFromFdno(fdno)
        except rpm.error:
            fdno = os.open(rpm_file, os.O_RDONLY)
            ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
            hdr = ts.hdrFromFdno(fdno)
        os.close(fdno)
    else:
        mi = ts.dbMatch('name', pkg)
        hdr = next(mi)

    if options.isFile:
        print("WARNING: Parsing uninstalled RPM files is experimental")
    for f in rpm.files(hdr):
        p = {}
        if options.verbose:
            print("path: {}".format(f.name))
        p["path"] = f.name
        p["mode"] = f.mode
        p["filesystem"] = "root"
        p["user"] = f.user
        p["group"] = f.group
        if (f.name.startswith('/etc/systemd/system/') or
        f.name.startswith('/usr/lib/systemd/system/')):   
            mco["spec"]["config"]["systemd"]["units"].append(p)
        elif  (f.name.startswith('/etc/') or options.allFiles):
            mco["spec"]["config"]["storage"]["files"].append(p)
        try:
            p["contents"] = {}
            if options.isFile:
                pass
            else:
                p["contents"]["source"] = file_to_data(f.name)
        except IsADirectoryError:
            pass

    ymco = yaml.dump(mco, default_style='"')
    print(ymco)


if __name__ == '__main__':
    main()
