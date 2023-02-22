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
import os

import pecs

class Pec:
    def __init__(self, username, password, acquisition, case, path):
        self.username = username
        # TODO: implement secure password handling
        self.password = password
        self.path = path
        os.chdir(self.path)
        self.acquisition = acquisition
        self.case = case
        return

    def sendPec(self):
        #Informazioni sul messaggio
        subject = 'Report acquisizione ' + str(self.acquisition) + ' caso: ' + str(self.case)
        message = 'In allegato report e relativo timestamp dell''acquisizione ' + str(self.acquisition) +\
                  ' relativa al caso: ' + str(self.case)

        # Creazione del messaggio PEC
        pec_message = pecs.new_message(self.username, subject, message, self.username, self.password)

        pdf = self.path + 'acquisition_report.pdf'
        timestamp = self.path + 'timestamp.tsr'

        # Aggiunta dei file allegati
        with open(pdf, 'rb') as f1, open(timestamp, 'rb') as f2:
            pec_message.add_attachment(f1.read(), 'application/pdf', 'report.pdf')
            pec_message.add_attachment(f2.read(), 'application/octet-stream', 'timestamp.tsr')

        # Invio del messaggio PEC
        pec_client = pecs.new_client()
        pec_client.send_message(pec_message)

        print('PEC inviata con successo')