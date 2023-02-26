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
import os
from controller.verifyPec import verifyPec as verifyPecController
import pyzmail
from view.case import Case as CaseView
from common.error import ErrorMessage


class SearchPec:
    def __init__(self, pec, password, server, port, case_info):
        self.pec = pec
        self.password = password
        self.server = server
        self.port = port
        self.error_msg = ErrorMessage()
        self.case_info = case_info
        return

    def fetchPec(self):
        # Impostazioni di connessione
        imap_host = self.server
        imap_port = self.port
        username = self.pec
        password = self.password

        with imaplib.IMAP4_SSL(imap_host, imap_port) as server:
            #os.chdir()
            server.login(username, password)
            server.select('inbox')

            # cerca i messaggi di posta elettronica nella cartella PEC
            status, messages = server.search(None, "ALL")
            messages = messages[0].split(b" ")
            pecs = []
            for msg_id in messages:
                # scarica il messaggio di posta elettronica in formato raw
                status, raw_email = server.fetch(msg_id, "(RFC822)")
                raw_email = raw_email[0][1]
                message = pyzmail.PyzMessage.factory(raw_email)
                pecs.append(message)

        return pecs

    def verifyEml(self, uid, pecs, acquisition_directory):
        message = None
        directory = str(acquisition_directory)
        uidModified = uid[1:-3]
        for pec in pecs:
            text = pec.text_part.get_payload().decode(pec.text_part.charset)
            for linea in text.split('\n'):
                if linea.startswith("Messaggio di posta certificata"):
                    for linea2 in text.split('\n'):
                        if linea2.startswith('Identificativo del messaggio:'):
                            uidFound = linea2.split(':')[-1].strip()
                            if uidFound == uidModified:
                                message = pec

        if not os.path.isdir(directory):
            # la cartella non esiste, quindi la creiamo
            os.makedirs(directory)
        os.chdir(directory)
        rawMessage = message.as_bytes()
        # salva il messaggio di posta elettronica in formato EML
        filename = f"{message.get('message-id')[1:-8]}.eml"  # utilizza l'ID del messaggio come nome del file EML
        with open(filename, "wb") as f:
            f.write(rawMessage)

        verifyPec = verifyPecController()
        path = directory+"/"+filename
        verifyPec.verifyPec(path)
        os.remove(directory+"/signature.txt")
        os.startfile(directory)



