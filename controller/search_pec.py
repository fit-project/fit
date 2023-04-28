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

import imaplib
import pyzmail

class SearchPec():

    def __init__(self, pec_email, password, imap_server, imap_port, case_info):
        self.pec_email = pec_email
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.case_info = case_info

    def fetch_pec(self, search_criteria):
        
        pecs = []

        with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as server:
            
            try:
                server.login(self.pec_email, self.password)
                server.select('inbox')
                status, messages = server.search(None, search_criteria)
                messages = messages[0].split(b" ")

                if str(messages) != "[b'']":
                    for msg_id in messages:
                        status, raw_email = server.fetch(msg_id, "(RFC822)")
                        raw_email = raw_email[0][1]
                        message = pyzmail.PyzMessage.factory(raw_email)
                        pecs.append(message)

            except imaplib.IMAP4.error as e:
                raise Exception(e)

        return pecs
