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

import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import re

class Revoke():
    def __init__(self, temp_x509):
        self.x509_file_path = temp_x509

    def check_is_revoked(self):
        is_revoked = False
        
        url = self.__extract_url() 
        if url:
            response = requests.get(url)  # Download CRL file
            crl_bytes = response.content  # Get CRL as byte string
            crl_base64 = base64.b64encode(crl_bytes).decode('utf-8') 
            crl_bytes = base64.b64decode(crl_base64)
            regex = r"\b([0-9a-fA-F]{2}:){15}[0-9a-fA-F]{2}\b"  

            with open(self.x509_file_path, "r") as f:
                for line in f:
                    match = re.search(regex, line)
                    if match:
                        serial_number = match.group()
                        break

            is_revoked = self.__analyze_CRL(crl_bytes, serial_number)

        return is_revoked

    def __extract_url(self):
        url = None
        with open(self.x509_file_path, 'r') as fp:
            lines = fp.readlines()
            for row in lines:
                word = 'URI:http'
                if row.find(word) != -1:
                    if "CRL" in row:
                        url = row
        if url:
            url = url.split("URI:")[1]
            url = url.strip()
            
        return url

    def __analyze_CRL(self, crl_bytes, serial_number):
        crl = x509.load_der_x509_crl(crl_bytes, default_backend())
        found = False
        for revoked_cert in crl:
            if revoked_cert.serial_number == serial_number:
                found = True # The serial is present in the revoked list
                break

        return found

    