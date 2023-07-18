#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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
                        status, raw_email = server.fetch(msg_id, "BODY.PEEK[HEADER]")
                        raw_email = raw_email[0][1]
                        message = pyzmail.PyzMessage.factory(raw_email)
                        pecs.append(message)

            except imaplib.IMAP4.error as e:
                raise Exception(e)

        return pecs
