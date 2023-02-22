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
import hashlib
import os

import requests
import rfc3161ng
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from pyasn1.codec.der import encoder,decoder

from view.error import Error as ErrorView

from common.error import ErrorMessage


class Timestamp(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.error_msg = ErrorMessage()
        self.options = None

    def set_options(self, options):

        self.server_name = options['server_name']
        self.cert_url = options['cert_url']

    def apply_timestamp(self, acquisition_folder, pdf_filename):
        pdf_path = os.path.join(acquisition_folder, pdf_filename)
        ts_path = os.path.join(acquisition_folder, 'timestamp.tsr')
        cert_path = os.path.join(acquisition_folder, 'tsa.crt')

        # getting the chain from the authority
        response = requests.get(self.cert_url)
        with open(cert_path, 'wb') as f:
            f.write(response.content)

        certificate = open(cert_path, 'rb').read()

        # create the object
        rt = rfc3161ng.RemoteTimestamper(self.server_name, certificate=certificate)

        # file to be certificated
        with open(pdf_path, 'rb') as f:
            timestamp = rt.timestamp(data=f.read())

        # saving the timestamp
        timestamp_path = os.path.join(ts_path)
        with open(timestamp_path, 'wb') as f:
            f.write(timestamp)
        return