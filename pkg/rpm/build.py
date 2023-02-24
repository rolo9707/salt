#! /bin/env python

import argparse
import os
import sys
import tarfile
from os.path import abspath, dirname, join
from shutil import copy
from subprocess import check_call

parser = argparse.ArgumentParser(description="Build salt rpms")
parser.add_argument(
    "buildid",
    help="The build id to use i.e. the bit after the salt version in the package name",
)
args = parser.parse_args()

src = abspath(join(dirname(__file__), "../.."))

sys.path.append(src)

import salt.version  # isort:skip

salt_version = salt.version.__saltstack_version__.string

rpmbuild = join(os.environ["HOME"], "rpmbuild")
copy(join(src, "pkg/rpm/salt.spec"), join(rpmbuild, "SPECS"))
for f in os.listdir(join(src, "pkg/rpm")):
    if f in ["salt.spec", "build.py"]:
        continue
    copy(join(src, "pkg/rpm", f), join(rpmbuild, "SOURCES"))


def srcfilter(ti):
    return None if "/.git" in ti.name else ti


with tarfile.open(join(rpmbuild, f"SOURCES/salt-{salt_version}.tar.gz"), "w|gz") as tf:
    tf.add(src, arcname=f"salt-{salt_version}", filter=srcfilter)


cmd = [
    "rpmbuild",
    "-bb",
    f"--define=salt_version {salt_version}",
    f"--define=buildid {args.buildid}",
    "salt.spec",
]
print(f"""Executing: {" ".join(f'"{c}"' for c in cmd)}""")
check_call(cmd, cwd=join(rpmbuild, "SPECS"))
