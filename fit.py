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
from view.web.web import Web as WebView

# from view.mail import Mail as MailView
# from view.instagram import Instagram as InstagramView

# from view.verify_pec import VerifyPec as VerifyPecView

# from view.verify_pdf_timestamp import VerifyPDFTimestamp as VerifyPDFTimestampView
# from view.video import Video as VideoView


if __name__ == "__main__":
    app = QApplication(sys.argv)

    init = InitView()

    wizard = WizardView()
    wizard.init_wizard()

    web = WebView()
    web.hide()

    # mail = MailView()
    # mail.hide()

    # insta = InstagramView()
    # insta.hide()

    # timestamp = VerifyPDFTimestampView()
    # timestamp.hide()

    # pec = VerifyPecView()
    # pec.hide()

    # video = VideoView()
    # video.hide()

    def start_task(task, case_info):
        options = {}
        if task == "web":
            acquisition_window = web
        elif task == "mail":
            acquisition_window = mail
        elif task == "insta":
            acquisition_window = insta
        elif task == "timestamp":
            acquisition_window = timestamp
        elif task == "video":
            acquisition_window = video
        elif task == "pec":
            acquisition_window = pec

        acquisition_window.init(case_info, wizard, options)
        acquisition_window.show()

    # Wizard sends a signal when finish button is clicked and case is stored on the DB
    wizard.finished.connect(lambda task, case_info: start_task(task, case_info))

    init.init_check()
    wizard.show()
    sys.exit(app.exec())
