#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import datetime
import os
import email
import imaplib
import smtplib
import pyzmail

from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from common.constants.controller.pec import *

class Pec():
    def __init__(self, pec_email, password, acquisition_type, case_info, acquisition_directory, smtp_server, smtp_port, imap_server, imap_port):
        self.pec_email = pec_email
        # TODO: implement secure password handling
        self.password = password
        self.acquisition_directory = acquisition_directory
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.acquisition_type = acquisition_type
        self.case_info = case_info
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.timestamp = None
        self.subject = None


    def send_pec(self):

        # subject and body of message
        now = datetime.datetime.now()
        self.timestamp = now.timestamp()
        self.subject = SUBJECT.format(str(self.acquisition_type), str(self.case_info), str(self.timestamp))
        body = BODY.format(str(self.acquisition_type), str(self.case_info))

        # Make message
        msg = MIMEMultipart()
        msg['From'] = self.pec_email
        msg['To'] = self.pec_email
        msg['Subject'] = self.subject
        msg.attach(MIMEText(body, 'plain'))

        pdf = os.path.join(self.acquisition_directory, 'acquisition_report.pdf')
        tsr = os.path.join(self.acquisition_directory, 'timestamp.tsr')
        crt = os.path.join(self.acquisition_directory, 'tsa.crt')

        # Attach PDF Report
        with open(pdf, "rb") as f:
            attach_pdf = MIMEApplication(f.read(), _subtype="pdf")
            attach_pdf.add_header('content-disposition', 'attachment', filename="report.pdf")
            msg.attach(attach_pdf)

        # Attach TSR file
        with open(tsr, "rb") as f:
            attach_tsr = MIMEApplication(f.read(), _subtype="tsr")
            attach_tsr.add_header('content-disposition', 'attachment', filename="timestamp.tsr")
            msg.attach(attach_tsr)

        # Attach CRT file
        with open(crt, "rb") as f:
            attach_tsr = MIMEApplication(f.read(), _subtype="crt")
            attach_tsr.add_header('content-disposition', 'attachment', filename="tsa.crt")
            msg.attach(attach_tsr)

        try:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.pec_email, self.password)
            server.sendmail(self.pec_email, self.pec_email, msg.as_string())
        except Exception as e:
            raise Exception(e)
    

    def retrieve_eml(self):
        
        if self.timestamp is None:
            return
        find_it = False

        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            server.login(self.pec_email, self.password)
            server.select('inbox')

            messages = self.__search_message(server)
            if str(messages) != "[b'']":
                find_it = True
                self.__save_message(server, messages[0])
        except Exception as e:
             raise Exception(e)

        return find_it
    
    def __search_message(self, server):
        subject = 'POSTA CERTIFICATA: ' + self.subject
        search_criteria = f'SUBJECT "{subject}"'
        status, messages = server.search(None, search_criteria)
        return messages[0].split(b" ")
    
    def __save_message(self, server, message):
        # download the email message in raw format
        status, raw_email = server.fetch(message, "(RFC822)")
        pec_data = raw_email[0][1]

        # check the PEC using the email library
        pec_message = email.message_from_bytes(pec_data)
        message = pyzmail.PyzMessage.factory(pec_data)

        digital_id_name = pec_message.get('X-Digital-ID', '')

        # add digital id name to the PEC
        pec_data = pec_data.replace(b'\r\n\r\n', f'\r\nX-Digital-ID:'
                                                    f' {digital_id_name}\r\n\r\n'.encode(), 1)
        
        filename = f"{message.get('message-id')[1:-8]}.eml"
        filename = os.path.join(self.acquisition_directory, filename)

        # save EML file
        with open(filename, 'wb') as f:
            f.write(pec_data)