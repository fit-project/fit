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
import glob
import hashlib
import imaplib
import os
import zipfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import rfc3161ng
import smtplib
from email.message import EmailMessage


class Timestamp:

    def sendMessage(self, email, password, server, port, file, caseNumber):
        SERVER = server
        PORT = port
        SENDER = email
        PASSWORD = password
        RECEIVER = email
        SUBJECT = "Report case: " + str(caseNumber)
        CONTENT = "In allegato il report del caso " + str(caseNumber)
        FILE_PATH = file

        msg = MIMEMultipart()
        msg['Subject'] = SUBJECT
        msg['From'] = SENDER
        msg['To'] = RECEIVER
        msg.attach(MIMEText(CONTENT, 'plain'))

        # apertura file in binario
        with open(FILE_PATH, "rb") as attachment:
            # aggiunta header con nome del file zip
            part = MIMEBase("acquisizione", "zip")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        fileName = os.path.basename(FILE_PATH)

        # aggiunta header con nome del file zip
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {fileName}",
        )

        # aggiunta allegato al messaggio e conversione in string
        msg.attach(part)
        text = msg.as_string()
        server = smtplib.SMTP_SSL(SERVER, PORT)
        # server.set_debuglevel(1)  # per stampare info sul debug
        # server.starttls()
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, text)
        print("Email inviata con successo")

    def verifyTimestamp(self, email, password, server, caseNumber):
        SERVER = server
        MAIL = email
        PASSWORD = password
        CASENUMBER = caseNumber

        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(MAIL, PASSWORD)
        mail.select("inbox")

        subject = "Report case: " + str(CASENUMBER)
        result, data = mail.search(None, '(FROM "{}" SUBJECT "{}")'.format(MAIL, subject))

        ids = data[0].split()

        if ids:
            # email found
            for id in ids:
                result, data = mail.fetch(id, "(RFC822)")
                raw_email = data[0][1].decode("utf-8")
                email_message = email.message_from_string(raw_email)
                os.chdir("C:\\Users\\domen\\Desktop\\test\\")
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    file_name = part.get_filename()
                    if bool(file_name):
                        # allegato trovato
                        file_data = part.get_payload(decode=True)
                        if file_data:
                            with open(file_name, 'wb') as f:
                                f.write(file_data)
                                # allegato scaricato
                    with zipfile.ZipFile(file_name, "r") as zip_ref:
                        zip_ref.extractall("output_folder")
                        # estratto
        else:
            pass

        mail.close()
        mail.logout()

        pathPdf = "C:\\Users\\domen\\Desktop\\test\\output_folder\\*.pdf"
        certificate = open('cert/tsa.crt', 'rb').read()
        rt = rfc3161ng.RemoteTimestamper('http://freetsa.org/tsr', certificate=certificate)

        foundPdf = glob.glob(pathPdf)
        for pdf in foundPdf:
            pathTsr = "C:\\Users\\domen\\Desktop\\test\\output_folder\\*.tsr"
            founfTsr = glob.glob(pathTsr)
        for tsr in founfTsr:
            hexdigest = hashlib.sha256(pdf.read()).hexdigest()
            check = rt.check(tsr, data=hexdigest.encode('utf-8'))
        if check:
            print("timestamp valido")
        else:
            print("timestamp non valido")

    def test(self):
        import email
        import glob
        import hashlib
        import imaplib
        import os
        import smtplib
        import zipfile
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        import requests
        import rfc3161ng

        if __name__ == '__main__':
            filename = "C:\\Users\\domen\\Desktop\\tirocinio.txt"
            url = "https://api.timestampapi.com/api/v1/timestamp"

            with open(filename, "rb") as f:
                file_data = f.read()
            payload = {"data": file_data.hex()}
            response = requests.post(url, json=payload)

            if response.ok:
                timestamp = response.json()["timestamp"]
                print("Il file", filename, "ha un timestamp certificato del", timestamp)
            else:
                print("Impossibile ottenere un timestamp certificato per il file.", filename)
