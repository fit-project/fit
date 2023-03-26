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
import datetime
import email
import imaplib
import os
import smtplib
import subprocess
import uuid
from email import policy
from email.generator import Generator
from email.message import Message
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import OpenSSL
import pyzmail
from OpenSSL import crypto

from view.error import Error as ErrorView
from PyQt5 import QtWidgets
from email.mime.multipart import MIMEMultipart
from common.error import ErrorMessage
from controller.searchPec import SearchPec as SearchPecController

class Pec:
    def __init__(self, username, password, acquisition, case, path, server, port, serverImap, portImap):
        self.username = username
        # TODO: implement secure password handling
        self.password = password
        self.path = path
        self.server = server
        self.port = port
        os.chdir(str(self.path))
        self.acquisition = acquisition
        self.case = case
        self.error_msg = ErrorMessage()
        self.serverImap = serverImap
        self.portImap = portImap
        return



    def sendPec(self):
        results = []
        error = False
        email_utente = self.username
        password_utente = self.password
        smtp_server = self.server
        smtp_port = self.port

        # Destinatario, oggetto e contenuto del messaggio
        destinatario = self.username
        todayDate = datetime.datetime.now()
        timestampDate = todayDate.timestamp()
        oggetto = 'Report acquisizione ' + str(self.acquisition) + ' caso: ' + str(self.case) + ' ID: ' + \
                  str(timestampDate)
        contenuto = 'In allegato report e relativo timestamp dell\' acquisizione ' + str(self.acquisition) + \
                    ' relativa al caso: ' + str(self.case)

        # Costruzione del messaggio email
        msg = MIMEMultipart()
        msg['From'] = email_utente
        msg['To'] = destinatario
        msg['Subject'] = oggetto
        msg.attach(MIMEText(contenuto, 'plain'))

        pdf = str(self.path) + '/acquisition_report.pdf'
        timestamp = str(self.path) + '/timestamp.tsr'

        # Aggiunta di un file PDF come allegato
        with open(pdf, "rb") as f:
            allegato_pdf = MIMEApplication(f.read(), _subtype="pdf")
            allegato_pdf.add_header('content-disposition', 'attachment', filename="report.pdf")
            msg.attach(allegato_pdf)

        # Aggiunta di un file TSR come allegato
        with open(timestamp, "rb") as f:
            allegato_tsr = MIMEApplication(f.read(), _subtype="tsr")
            allegato_tsr.add_header('content-disposition', 'attachment', filename="timestamp.tsr")
            msg.attach(allegato_tsr)

        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(email_utente, password_utente)
            server.sendmail(email_utente, destinatario, msg.as_string())
        except Exception:
            error = True
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['pec_error'],
                                  self.error_msg.MESSAGES['pec_error'],
                                  'Wrong SMTP or PEC parameters or credentials')
            error_dlg.exec_()
        results.append(timestampDate)
        results.append(error)
        return results
    def retrieveEml(self, timestampDate):

        error = False
        find = False
        results = []

        try:
            server = imaplib.IMAP4_SSL(self.serverImap, self.portImap)
            server.login(self.username, self.password)
            server.select('inbox')
        except Exception:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['pec_error'],
                                  self.error_msg.MESSAGES['pec_error'],
                                  'Wrong IMAP or PEC parameters or credentials')
            error = True
            error_dlg.exec_()

        if error == True:
            pass
        else:
            # cerca i messaggi di posta elettronica nella cartella PEC
            oggetto = 'POSTA CERTIFICATA: Report acquisizione ' + str(self.acquisition) + ' caso: ' +\
                      str(self.case) + ' ID: ' + str(timestampDate)
            oggettoStr = str(oggetto)
            searchCriteria = f'SUBJECT "{oggettoStr}"'
            status, messages = server.search(None, searchCriteria)
            messages = messages[0].split(b" ")
            if str(messages) == "[b'']":
                pass
            else:
                find = True
                # scarica il messaggio di posta elettronica in formato raw
                status, raw_email = server.fetch(messages[0], "(RFC822)")
                pec_data = raw_email[0][1]

                # analizzare la PEC utilizzando la libreria email
                pec_message = email.message_from_bytes(pec_data)
                message = pyzmail.PyzMessage.factory(pec_data)

                # ottenere il nome dell'ID digitale
                nome_id_digitale = pec_message.get('X-Digital-ID', '')

                # aggiungere il nome dell'ID digitale alla PEC
                pec_data = pec_data.replace(b'\r\n\r\n', f'\r\nX-Digital-ID:'
                                                           f' {nome_id_digitale}\r\n\r\n'.encode(), 1)

                filename = f"{message.get('message-id')[1:-8]}.eml"
                # salvare la PEC sul disco
                with open(filename, 'wb') as f:
                    f.write(pec_data)


        results.append(error)
        results.append(find)
        return results
