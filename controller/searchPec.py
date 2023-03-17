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
import email
import imaplib
import os
from controller.integrityPec.verifyPec import verifyPec as verifyPecController
import pyzmail
from common.error import ErrorMessage
from PyQt5 import QtWidgets
from view.error import Error as ErrorView


class SearchPec:
    def __init__(self, pec, password, server, port, case_info):
        self.pec = pec
        self.password = password
        self.server = server
        self.port = port
        self.error_msg = ErrorMessage()
        self.case_info = case_info
        return

    def fetchPec(self, searchCriteria):
        error = False
        pecsToShow = []
        # Impostazioni di connessione
        imap_host = self.server
        imap_port = self.port
        username = self.pec
        password = self.password

        with imaplib.IMAP4_SSL(imap_host, imap_port) as server:
            try:
                server.login(username, password)
                server.select('inbox')
            except imaplib.IMAP4.error:
                error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                      self.error_msg.TITLES['pec_error'],
                                      self.error_msg.MESSAGES['pec_error'],
                                      'Wrong parameters or credentials')
                error = True
                error_dlg.exec_()

            if error == True:
                pass
            else:
                status, messages = server.search(None, searchCriteria)
                messages = messages[0].split(b" ")
                pecs = []
                pecsToShow = []
                if str(messages) == "[b'']":
                    pass
                else:
                    for msg_id in messages:
                        # scarica il messaggio di posta elettronica in formato raw
                        status, raw_email = server.fetch(msg_id, "(RFC822)")
                        raw_email = raw_email[0][1]
                        message = pyzmail.PyzMessage.factory(raw_email)
                        pecsToShow.append(message)
        return pecsToShow
