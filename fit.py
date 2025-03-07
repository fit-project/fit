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
import signal

from PyQt6 import QtWidgets, QtGui
from common.utility import resolve_path, get_platform

from view.wizard import Wizard as WizardView
from view.scrapers.web.web import Web as WebView
from view.scrapers.mail.mail import Mail as MailView
from view.scrapers.instagram.instagram import Instagram as InstagramView
from view.scrapers.video.video import Video as VideoView
from view.scrapers.entire_website.entire_website import (
    EntireWebsite as EntireWebsiteView,
)


class FitApplication(QtWidgets.QApplication):
    def __init__(self, argv, fit_bootstrap_pid):
        super().__init__(argv)
        self.fit_bootstrap_pid = fit_bootstrap_pid


class FitWizard(WizardView):
    def __init__(self, fit_bootstrap_pid):
        super().__init__()
        self.fit_bootstrap_pid = fit_bootstrap_pid

    def showEvent(self, event):
        super().showEvent(event)
        if self.fit_bootstrap_pid:
            print("Finestra di Fit visibile! Notifico fit-bootstrap...")
            os.kill(self.fit_bootstrap_pid, signal.SIGTERM)


if __name__ == "__main__":
    fit_bootstrap_pid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    app = FitApplication(sys.argv, fit_bootstrap_pid)

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
    wizard.show()

    # Wizard sends a signal when start button is clicked and case is stored on the DB
    wizard.finished.connect(lambda task, case_info: start_task(task, case_info))

    sys.exit(app.exec())
