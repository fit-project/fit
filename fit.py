#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import sys
import ctypes
import os
import stat
import sys
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
from common.utility import resolve_path, get_platform


def get_shared_temp_dir():
    if get_platform() == "win":
        return "C:\\ProgramData\\fit-bootstrap"
    else:
        return "/var/tmp/fit-bootstrap"


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
    fit_bootstrap_pid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    user_type = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "null" else None
    ffmpeg_flag = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "null" else None
    npcap_flag = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "null" else None

    app = FitApplication(
        sys.argv, fit_bootstrap_pid, user_type, ffmpeg_flag, npcap_flag
    )

    fit_bootstrap_pid = None

    if get_platform() == "win":
        app_id = "org.fit-project.fit"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app.setWindowIcon(QtGui.QIcon(resolve_path("icon.ico")))

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
