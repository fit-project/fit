#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os
from datetime import datetime
from controller.verify_pec.html_2_pdf import Html2Pdf

from common.constants.controller.generate_report import *


class GenerateReport:

    def pdf_creator(self, report_info):
        
        signature = SIGNATURE_NOT_EXIST
        if report_info.get('is_signature') == True:
            signature = SIGNATURE_EXIST

        integrity = INTEGRITY_FAIL
        if report_info.get('is_integrity') == True:
            integrity = INTEGRITY_SUCCESS

        provider_name = report_info.get('provider_name')
        is_on_agid_list = PROVIDER_IS_NOT_ON_AGID_LIST.format(provider_name)
        if report_info.get('is_on_agid_list') == True:
            is_on_agid_list = PROVIDER_IS_ON_AGID_LIST.format(provider_name)

        revoked = PEC_ADDRESS_IS_NOT_REVOKED
        if report_info.get('is_revoked') == True:
            revoked = PEC_ADDRESS_IS_REVOKED

        self.__generate(
            report_info.get('to'),
            report_info.get('reply_to'),
            report_info.get('subject'),
            report_info.get('send_date'),
            report_info.get('expiration_date'),
            integrity,
            revoked,
            signature,
            provider_name,
            is_on_agid_list,
            report_info.get('case_info'),
            report_info.get('ntp'),
            report_info.get('eml_file_path'),
        )

    def __generate(self, to, replay_to, subject, send_date, expiration_date,
                                     integrità, revoked, signature, provider_name, is_on_agid_list, case_info,
                                     ntp, eml_file_path):


        case_index = subject.find("caso: ")
        case_slice_before = subject[:case_index]
        case_slice_after = subject[case_index:]
        subject = case_slice_before + "\n" + case_slice_after

        folder = os.path.dirname(eml_file_path)
        info_file_path = f'{folder}/pec_info.txt'
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(info_file_path, 'w') as file:
            file.write(f'{REPORT_LABEL_DETAILS}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_TO}\n')
            file.write(f'{to}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_REPLAY_TO}\n')
            file.write(f'{replay_to}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_SUBJECT}\n')
            file.write(f'{subject}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_SEND_DATE}\n')
            file.write(f'{send_date}\n')
            file.write('======================================================================\n')
            file.write(f'\n')
            file.write(f'{REPORT_LABEL_RESULTS}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_EXPIRATION_DATE}\n')
            file.write(f'{expiration_date}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_SIGNATURE}\n')
            file.write(f'{signature}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_INTEGRITY}\n')
            file.write(f'{integrità}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_REVOKED}\n')
            file.write(f'{revoked}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_PROVIDER_NAME}\n')
            file.write(f'{provider_name}\n')
            file.write('======================================================================\n')
            file.write(f'{REPORT_LABEL_PROVIDER_CHECK}\n')
            file.write(f'{is_on_agid_list}\n')
            file.write('======================================================================\n')

        report = Html2Pdf(folder, case_info, ntp)
        report.generate_pdf(True, info_file_path)
