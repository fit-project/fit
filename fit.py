#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2022 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys
from view.wizard import Wizard as WizardView
from view.web import Web as WebView
from view.mail import Mail as MailView
from view.instagram import Instagram as InstagramView
from view.verify_pdf_timestamp import VerifyPDFTimestamp as VerifyPDFTimestampView

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wizard = WizardView()
    wizard.init_wizard()
    web = WebView()
    web.hide()
    mail = MailView()
    mail.hide()
    insta = InstagramView()
    insta.hide()
    timestamp = VerifyPDFTimestampView()
    timestamp.hide()

    
    def start_task(task, case_info):
        if (task == 'web'):
            acquisition_window = web
        elif (task == 'mail'):
            acquisition_window = mail
        elif (task == 'fb'):
            pass
        elif (task == 'insta'):
            acquisition_window = insta
        elif (task == 'timestamp'):
            acquisition_window = timestamp

        acquisition_window.init(case_info)
        acquisition_window.show()

    #Wizard sends a signal when finish button is clicked and case is stored on the DB
    wizard.finished.connect(lambda task, case_info: start_task(task, case_info))

    wizard.show()

    sys.exit(app.exec_())