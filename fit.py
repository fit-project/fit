#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import sys
from PyQt6.QtWidgets import QApplication

from view.init import Init as InitView
from view.wizard import Wizard as WizardView
from view.scrapers.web.web import Web as WebView
from view.scrapers.mail.mail import Mail as MailView
from view.scrapers.instagram.instagram import Instagram as InstagramView
from view.scrapers.video.video import Video as VideoView

from view.verify_pec import VerifyPec as VerifyPecView
from view.verify_pdf_timestamp import VerifyPDFTimestamp as VerifyPDFTimestampView
from view.entire_website.entire_website import EntireWebsite as EntireWebsiteView

if __name__ == "__main__":
    app = QApplication(sys.argv)

    init = InitView()
    wizard = WizardView()
    wizard.init_wizard()
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
        elif task == "verify_timestamp":
            acquisition_window = VerifyPDFTimestampView()
        elif task == "verify_pec":
            acquisition_window = VerifyPecView()

        acquisition_window.init(case_info, wizard, options)
        acquisition_window.show()

    # Wizard sends a signal when finish button is clicked and case is stored on the DB
    wizard.finished.connect(lambda task, case_info: start_task(task, case_info))

    # init.init_check()
    wizard.show()
    sys.exit(app.exec())
