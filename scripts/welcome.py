#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import locale
import os
import subprocess
from dialog import Dialog, PythonDialogBug

locale.setlocale(locale.LC_ALL, '')


def gns3_version():
    """
    Return the GNS3 server version
    """
    try:
        return subprocess.check_output(["gns3server", "--version"]).strip().decode()
    except subprocess.CalledProcessError:
        return ""


d = Dialog(dialog="dialog", autowidgetsize=True)
d.set_background_title("GNS3 {}".format(gns3_version()))


def mode():
    if d.yesno("This feature is for testers only. You can break your GNS3 install. Are you REALLY sure you want to continue?", yes_label="Exit (Safe option)", no_label="Continue") == d.OK:
        return
    d.msgbox("You have been warned...")
    code, tag = d.menu("Select the GNS3 version",
                       choices=[("Stable", "Last stable GNS3 version RECOMMENDED"),
                                ("Testing", "Next stable release"),
                                ("Unstable", "Totaly unstable version")])
    d.clear()
    if code == Dialog.OK:
        os.makedirs(os.path.expanduser("~/.config/gns3"), exist_ok=True)
        with open(os.path.expanduser("~/.config/gns3/gns3_release"), "w+") as f:
            if tag == "Stable":
                f.write("stable")
            elif tag == "Testing":
                f.write("testing")
            elif tag == "Unstable":
                f.write("unstable")
            else:
                assert False

        update(force=True)


def get_release():
    try:
        with open(os.path.expanduser("~/.config/gns3/gns3_release")) as f:
            return f.read()
    except OSError:
        return "stable"


def update(force=False):
    if not force:
        if d.yesno("The server will reboot at the end of the update process. Continue?") != d.OK:
            return
    if get_release() == "stable":
        os.system("curl https://raw.githubusercontent.com/GNS3/gns3-vm/master/scripts/update.sh |bash && sudo reboot")
    elif get_release() == "testing":
        os.system("curl https://raw.githubusercontent.com/GNS3/gns3-vm/master/scripts/update_testing.sh |bash && sudo reboot")
    elif get_release() == "unstable":
        os.system("curl https://raw.githubusercontent.com/GNS3/gns3-vm/master/scripts/update_unstable.sh |bash && sudo reboot")


def vm_information():
    """
    Show IP, SSH settings....
    """

    try:
        with open('/etc/issue') as f:
            content = f.read()
    except FileNotFoundError:
        content = """Welcome to GNS3 appliance"""

    content += "\nRelease channel: " + get_release()

    try:
        d.msgbox(content)
    # If it's an scp command or any bugs
    except:
        os.execvp("bash", ['/bin/bash'])

vm_information()

while True:
    code, tag = d.menu("GNS3 {}".format(gns3_version()),
                       choices=[("Information", "Display VM information"),
                        ("Update", "Update GNS3"),
                        ("Shell", "Open a console"),
                        ("Version", "Select the GNS3 version"),
                        ("Reboot", "Reboot the VM"),
                        ("Shutdown", "Shutdown the VM")])
    d.clear()
    if code == Dialog.OK:
        if tag == "Shell":
            os.execvp("bash", ['/bin/bash'])
        elif tag == "Version":
            mode()
        elif tag == "Reboot":
            os.execvp("sudo", ['/usr/bin/sudo', "reboot"])
        elif tag == "Shutdown":
            os.execvp("sudo", ['/usr/bin/sudo', "poweroff"])
        elif tag == "Update":
            update()
        elif tag == "Information":
            vm_information()
