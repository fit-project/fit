#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import sys
import argparse
import ctypes
import os
import stat
import subprocess

from PyQt6 import QtWidgets, QtGui

from view.wizard import Wizard as WizardView
from view.scrapers.web.web import Web as WebView
from view.scrapers.mail.mail import Mail as MailView
from view.scrapers.instagram.instagram import Instagram as InstagramView
from view.scrapers.video.video import Video as VideoView
from view.scrapers.entire_website.entire_website import (
    EntireWebsite as EntireWebsiteView,
)

from view.util import disable_network_functionality, enable_network_functionality
from common.utility import resolve_path, get_platform, debug_log
import common.config_debug


import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Start FIT application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "fit_bootstrap_pid",
        nargs="?",
        type=int,
        default=None,
        help="FIT bootstrap process ID (default: None)",
    )

    parser.add_argument(
        "user_type",
        nargs="?",
        choices=["user", "admin"],
        default="user",
        help="Specify user privileges:\n"
        "- 'user' (default): Standard user mode.\n"
        "- 'admin': The user executing FIT has administrative privileges.\n"
        "  If not running as admin, it will not be possible to capture network traffic and execute traceroute.",
    )

    parser.add_argument(
        "--with-ffmpeg",
        action="store_true",
        help="Enable FFmpeg support for media processing.",
    )

    parser.add_argument(
        "--without-ffmpeg",
        action="store_true",
        help="Disable FFmpeg support (default).",
    )

    if get_platform() == "win":
        parser.add_argument(
            "--with-npcap",
            action="store_true",
            help="Enable Npcap support (only on Windows) to capture network traffic.",
        )

        parser.add_argument(
            "--without-npcap",
            action="store_true",
            help="Disable Npcap support (default, only on Windows). Without Npcap, it will not be possible to capture network traffic.",
        )

    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")

    args = parser.parse_args()

    ffmpeg_flag = "--with-ffmpeg" if args.with_ffmpeg else "--without-ffmpeg"

    npcap_flag = "--without-npcap"
    if get_platform() == "win":
        npcap_flag = "--with-npcap" if args.with_npcap else "--without-npcap"

    if args.debug:
        common.config_debug.set_debug_mode(True)

    return args.fit_bootstrap_pid, args.user_type, ffmpeg_flag, npcap_flag


def get_shared_temp_dir():
    return (
        "C:\\ProgramData\\fit-bootstrap"
        if get_platform() == "win"
        else "/var/tmp/fit-bootstrap"
    )


def notify_fit_bootstrap(fit_bootstrap_pid):
    temp_dir = get_shared_temp_dir()
    os.makedirs(temp_dir, exist_ok=True)
    ready_file = os.path.join(temp_dir, f"fit_ready_{fit_bootstrap_pid}")

    try:
        with open(ready_file, "w") as f:
            f.write("ready")

        if get_platform() == "win":
            subprocess.run(["icacls", ready_file, "/grant", "Everyone:F"], check=True)
        else:
            os.chmod(ready_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    except Exception as e:
        pass


class FitApplication(QtWidgets.QApplication):
    def __init__(self, argv, fit_bootstrap_pid, user_type, ffmpeg_flag, npcap_flag):
        super().__init__(argv)
        self.fit_bootstrap_pid = fit_bootstrap_pid
        self.user_type = user_type
        self.ffmpeg_flag = ffmpeg_flag
        self.npcap_flag = npcap_flag


class FitWizard(WizardView):
    def __init__(self, fit_bootstrap_pid):
        super().__init__()
        self.fit_bootstrap_pid = fit_bootstrap_pid

    def showEvent(self, event):
        super().showEvent(event)
        if self.fit_bootstrap_pid:
            notify_fit_bootstrap(self.fit_bootstrap_pid)


if __name__ == "__main__":
    fit_bootstrap_pid, user_type, ffmpeg_flag, npcap_flag = parse_args()

    app = FitApplication(
        sys.argv, fit_bootstrap_pid, user_type, ffmpeg_flag, npcap_flag
    )

    if get_platform() == "win":
        app_id = "org.fit-project.fit"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app.setWindowIcon(QtGui.QIcon(resolve_path("icon.ico")))

    debug_log("Starting fit...")

    acquisition_window = None

    def start_task(task, case_info):
        global acquisition_window
        options = {}

        if task == "web":
            acquisition_window = WebView()
        elif task == "mail":
            acquisition_window = MailView()
        elif task == "instagram":
            acquisition_window = InstagramView()
        elif task == "video":
            acquisition_window = VideoView()
        elif task == "entire_website":
            acquisition_window = EntireWebsiteView()

        acquisition_window.init(case_info, wizard, options)
        acquisition_window.show()

    wizard = FitWizard(fit_bootstrap_pid)

    if user_type == "admin" and npcap_flag != "--no-npcap":
        enable_network_functionality()
    else:
        disable_network_functionality()

    wizard.show()

    # Wizard sends a signal when start button is clicked and case is stored on the DB
    wizard.finished.connect(lambda task, case_info: start_task(task, case_info))

    sys.exit(app.exec())
