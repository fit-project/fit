#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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

    