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
import email
import tempfile
import os

from controller.verify_pec.expiration_date import ExpirationDate
from controller.verify_pec.revoke import Revoke
from controller.verify_pec.authority import Authority
from controller.verify_pec.generate_report import GenerateReport

class verifyPec():

    def __init__(self):
        self.temp_x509 = os.path.join(tempfile.gettempdir(), 'tmp_x509')
        self.temp_pem = os.path.join(tempfile.gettempdir(), 'tmp_cert.pem')
        self.temp_textdata = os.path.join(tempfile.gettempdir(), 'tmp_textdata')
    
    def verify(self, eml_file_path, case_info, ntp):

        report_info = {'case_info':case_info, 'ntp':ntp, 'eml_file_path':eml_file_path}

        try:
            email_info = ExpirationDate().verify(eml_file_path, self.temp_pem, self.temp_x509, self.temp_textdata)
        except Exception as e:
            raise Exception(e)
        
        if len(email_info) > 0:
            # Check if signature exist
            signature = self.__signature_exist(eml_file_path)
            # Check if the PEC has been revoked
            revoke = Revoke(self.temp_x509)
            is_revoked = revoke.check_is_revoked()

            #Check autority
            authority = Authority(self.temp_x509)
            authority_name = authority.get_authority()
            is_on_agid_list = authority.check_if_authority_is_on_agid_list(authority_name)

            report_info.update(email_info)
            report_info.update(signature)
            report_info.update({'is_integrity' : True, 'is_revoked':is_revoked, 
                                'authority_name':authority_name, 'is_on_agid_list': is_on_agid_list})
        else:
            with open(eml_file_path, 'rb') as f:
                msg = email.message_from_binary_file(f)
            

            email_info = {'reply_to': msg['Reply-To'], 'to' : msg['To'], 
                'subject': msg['Subject'], 'send_date': msg['Date']}
            
            signature = self.__signature_exist(eml_file_path)

            report_info.update(email_info)
            report_info.update(signature)
            report_info.update({'is_integrity' : False, 'is_revoked': False, 
                                'authority_name':'', 'is_on_agid_list': False})
            

        GenerateReport().pdf_creator(report_info)



    def __signature_exist(self, eml_file_path):
        
        message_text = " "
        exist = False
        
        with open(eml_file_path, "r") as f:
            msg = email.message_from_file(f)
            
        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_type() == 'application/pkcs7-signature':
                    exist = True

            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    if part.get_content_charset() == 'utf-8' or part.get_content_charset() == 'UTF-8':
                        message_text = part.get_payload(decode=True).decode('iso-8859-1')

        return {'is_signature': exist, 'message_text': message_text}
