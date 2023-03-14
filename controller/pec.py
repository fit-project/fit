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
import imaplib
import os
import smtplib
import subprocess
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import pyzmail

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
        contenuto = 'In allegato report e relativo timestamp dell\' acquisizione ' + str(self.acquisition) +\
                  ' relativa al caso: ' + str(self.case)

        # Costruzione del messaggio email
        msg = MIMEMultipart()
        msg['From'] = email_utente
        msg['To'] = destinatario
        msg['Subject'] = oggetto
        msg.attach(MIMEText(contenuto, 'plain'))

        pdf = str(self.path)+'/acquisition_report.pdf'
        timestamp = str(self.path)+'/timestamp.tsr'

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

        # Connessione e invio del messaggio
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:

            try:
                server.login(email_utente, password_utente)
                dataToday = datetime.datetime.today()
                server.sendmail(email_utente, destinatario, msg.as_string())
            except smtplib.SMTPException:
                error = True
                error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                      self.error_msg.TITLES['pec_error'],
                                      self.error_msg.MESSAGES['pec_error'],
                                      'Wrong parameters or credentials')
                error_dlg.exec_()
        return timestampDate

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
                                  'Wrong parameters or credentials')
            error = True
            error_dlg.exec_()

        if error == True:
            pass
        else:
            # cerca i messaggi di posta elettronica nella cartella PEC
            oggetto = 'Report acquisizione ' + str(self.acquisition) + ' caso: ' + str(self.case) + ' ID: ' + \
                      str(timestampDate)
            oggettoStr = str(oggetto)
            searchCriteria = f'SUBJECT "{oggettoStr}"'
            status, messages = server.search(None, searchCriteria)
            messages = messages[0].split(b" ")
            if len(messages) < 3:
                pass
            else:
                pecs = []
                for msg_id in messages:
                    # scarica il messaggio di posta elettronica in formato raw
                    status, raw_email = server.fetch(msg_id, "(RFC822)")
                    raw_email = raw_email[0][1]
                    message = pyzmail.PyzMessage.factory(raw_email)
                    pecs.append(message)
                for pec in pecs:
                    if pec.get_subject().startswith("POSTA CERTIFICATA:"):
                        find = True
                        rawMessage = pec.as_bytes()
                        # salva il messaggio di posta elettronica in formato EML
                        filename = f"{pec.get('message-id')[1:-8]}.eml"

                        # utilizza l'ID del messaggio come nome del file EML
                        with open(filename, "wb") as f:
                            f.write(rawMessage)

        results.append(error)
        results.append(find)
        return results



