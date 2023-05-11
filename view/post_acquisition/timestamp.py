#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os

import requests
from rfc3161ng.api import RemoteTimestamper
from PyQt5.QtCore import QObject, pyqtSignal


class Timestamp(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
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
        rt = RemoteTimestamper(self.server_name, certificate=certificate, hashname='sha256')

        # file to be certificated
        with open(pdf_path, 'rb') as f:
            timestamp = rt.timestamp(data=f.read())

        # saving the timestamp
        timestamp_path = os.path.join(ts_path)
        with open(timestamp_path, 'wb') as f:
            f.write(timestamp)