#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import email
import tempfile
import os

from controller.verify_pec.expiration_date import ExpirationDate
from controller.verify_pec.revoke import Revoke
from controller.verify_pec.provider import Provider
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
            provider = Provider(self.temp_x509)
            provider_name = provider.get_provider_name()
            is_on_agid_list = provider.check_if_provider_is_on_agid_list(provider_name)

            report_info.update(email_info)
            report_info.update(signature)
            report_info.update({'is_integrity' : True, 'is_revoked':is_revoked, 
                                'provider_name':provider_name, 'is_on_agid_list': is_on_agid_list})
        else:
            with open(eml_file_path, 'rb') as f:
                msg = email.message_from_binary_file(f)
            

            email_info = {'reply_to': msg['Reply-To'], 'to' : msg['To'], 
                'subject': msg['Subject'], 'send_date': msg['Date']}
            
            signature = self.__signature_exist(eml_file_path)

            report_info.update(email_info)
            report_info.update(signature)
            report_info.update({'is_integrity' : False, 'is_revoked': False, 
                                'provider_name':'', 'is_on_agid_list': False})
            

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
