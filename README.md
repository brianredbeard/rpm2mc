# rpm2mc

## About

`rpm2mc.py` is a utility which takes a package name or RPM filename as an
argument and outputs a resulting OpenShift [MachineConfig][mco].  The intention
of this tool is to allow users to extend Red Hat Enterprise Linux CoreOS (aka
CoreOS) without modifying the base image.

## Usage

```
Usage: rpm2mc.py [options] RPM

Options:
  -h, --help  show this help message and exit
  -f, --file  read data from RPM
  -a, --all   store all files, not just configs and systemd units
  -v          increase verbosity of output
```

Let's say (for some bizarre reason) you had a need to add `zram` to CoreOS.  As
zram really only contains a bash script, a configuration file, and a systemd
unit it becomes trivial to convert this RPM to a MachineConfig:

```
$ rpm2mc.py zram
"apiVersion": "machineconfiguration.openshift.io/v1"
"kind": "MachineConfig"
"spec":
  "config":
    "ignition":
      "version": "2.2.0"
    "storage":
      "files":
      - "contents":
          "source": "data:text/plain;base64,IyBUaGUgZmFjdG9yIGlzIHRoZSBwZXJjZW50YWdlIG9mIHRvdGFsIHN5c3RlbSBSQU0gdG8gYWxsb2NhdGUgdG8gdGhlIFpSQU0gYmxvY2sgZGV2aWNlKHMpLgpGQUNUT1I9MgoKUFJJT1JJVFk9MTAwMAo="
        "filesystem": "root"
        "group": "root"
        "mode": !!int "33188"
        "path": "/etc/zram.conf"
        "user": "root"
    "systemd":
      "units":
      - "contents":
          "source": "data:;base64,W1VuaXRdCkRlc2NyaXB0aW9uPUVuYWJsZSBjb21wcmVzc2VkIHN3YXAgaW4gbWVtb3J5IHVzaW5nIHpyYW0KRGVmYXVsdERlcGVuZGVuY2llcz1ubwpCZWZvcmU9c3dhcC50YXJnZXQKCltTZXJ2aWNlXQpUeXBlPW9uZXNob3QKUmVtYWluQWZ0ZXJFeGl0PXllcwpUaW1lb3V0U3RhcnRTZWM9MzBzZWMKRXhlY1N0YXJ0PS91c3Ivc2Jpbi96cmFtc3RhcnQKRXhlY1N0b3A9L3Vzci9zYmluL3pyYW1zdG9wCgpbSW5zdGFsbF0KV2FudGVkQnk9c3dhcC50YXJnZXQK"
        "filesystem": "root"
        "group": "root"
        "mode": !!int "33188"
        "path": "/usr/lib/systemd/system/zram-swap.service"
        "user": "root"
```

The astute user will notice that we have not actually grabbed the "binary" (aka
the shell script).  We can capture this by adding the `-a` flag, but note we
will naively grab everything in the RPM, including things we don't care about
for hosts we will be managing (like the LICENSE file).


## Todo

Below are a list of "todo" items recommended by other users.  Patches for
features in this list or other suggestions are graciously accepted.

 - Automatically gzip large assets
 - Properly handle non files:
  - symbolic links
  - hard links
  - directories
 - Clean up handling of decimal/octal mode handling
 - Properly parse file content from RPM file 
 - Add mechanism to skip "documentation" (flagged in the RPM)

[mco]: https://github.com/openshift/machine-config-operator
<!--
vim: ts=2 sw=2 et tw=80
-->
