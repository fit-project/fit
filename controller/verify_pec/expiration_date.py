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
from common.utility import is_cmd, get_platform
from email import policy
from email.parser import BytesParser
from datetime import datetime
import subprocess
import os


class ExpirationDate():        
    
    def verify(self, eml_file_path, pem_file_path, x509_file_path, textdata_file_path):
        result = {}
        openssl = "openssl"
        is_installed_openssl = is_cmd(openssl)
        
        
        if is_installed_openssl is False:
            openssl = '.\ext_lib\openssl\{}\openssl'.format(get_platform())
        # extract pem certificate from eml
        extract_pem = subprocess.run(
            [openssl, "smime", "-verify", "-in", eml_file_path, "-noverify", "-signer", pem_file_path, "-out", textdata_file_path],
            capture_output=True, text=True)
        
        # Convert pem to x509
        if extract_pem.returncode == 0:
            output = extract_pem.stdout
            os.system('{} x509 -in {} -text > {}'.format(openssl, pem_file_path, x509_file_path))
            result = self.__check_date(eml_file_path, x509_file_path)
        else:
            raise Exception(extract_pem.stderr)
            
        return result


    def __check_date(self, eml_file_path, x509_file_path):
        date_s = None

        with open(x509_file_path, 'r') as fp:
            lines = fp.readlines()
            for row in lines:
                word = 'Not After'
                if row.find(word) != -1:
                    date_s = row

        with open(eml_file_path, 'rb') as fp:
            msg = BytesParser(policy=policy.default).parse(fp)


        #expiration date
        if date_s is not None:
            date_s = date_s.split(" : ")[1]
            date_s = date_s.split(" G")[0]
            date_s = datetime.strptime(date_s, '%b %d %I:%S:%M %Y')

        return {'expiration_date': date_s, 'reply_to': msg['Reply-To'], 'to' : msg['To'], 
                'subject': msg['Subject'], 'send_date': msg['Date']}


