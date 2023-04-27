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
from datetime import datetime
from controller.verify_pec.html_2_pdf import Html2Pdf


class GenerateReport:

    def pdf_creator(self, report_info):
        
        signature = "Il messaggio non presenta una firma digitale."
        if report_info.get('is_signature') == True:
            signature = "Il messaggio presenta una firma digitale."

        integrity = "Il messaggio e' stato alterato."
        if report_info.get('is_integrity') == True:
            integrity = "Il messaggio non e' stato alterato."

        is_on_agid_list = "L'ente non e' presente nell elenco dei gestori per certificati Agid"
        if report_info.get('is_on_agid_list') == True:
            is_on_agid_list = "L'ente e' presente nell elenco dei gestori pec certificiati Agid"

        revoked = "L'indirizzo non e' stato revocato."
        if report_info.get('is_revoked') == True:
            revoked = "L'indirizzo usato per inviare il messaggio e' stato revocato."

        today_date = datetime.today().strftime("%d %b, %Y")

        self.__generate(
            report_info.get('to'),
            report_info.get('reply_to'),
            report_info.get('subject'),
            report_info.get('send_date'),
            report_info.get('expiration_date'),
            integrity,
            revoked,
            signature,
            report_info.get('authority_name'),
            is_on_agid_list,
            report_info.get('case_info'),
            report_info.get('ntp'),
            report_info.get('eml_file_path'),
        )

    def __generate(self, to, replay_to, subject, send_date, data_scadenza,
                                     integrità, revoked, signature, authority_name, is_on_agid_list, case_info,
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
            file.write(f'DETTAGLI PEC:\n')
            file.write('======================================================================\n')
            file.write(f'MITTENTE\n')
            file.write(f'{to}\n')
            file.write('======================================================================\n')
            file.write(f'DESTINATARIO\n')
            file.write(f'{replay_to}\n')
            file.write('======================================================================\n')
            file.write(f'OGGETTO\n')
            file.write(f'{subject}\n')
            file.write('======================================================================\n')
            file.write(f'DATA INVIO\n')
            file.write(f'{send_date}\n')
            file.write('======================================================================\n')
            file.write(f'\n')
            file.write(f'RISULTATI:\n')
            file.write('======================================================================\n')
            file.write(f'DATA SCADENZA\n')
            file.write(f'{data_scadenza}\n')
            file.write('======================================================================\n')
            file.write(f'FIRMA DIGITALE\n')
            file.write(f'{signature}\n')
            file.write('======================================================================\n')
            file.write(f'INTEGRITA''\n')
            file.write(f'{integrità}\n')
            file.write('======================================================================\n')
            file.write(f'CRL\n')
            file.write(f'{revoked}\n')
            file.write('======================================================================\n')
            file.write(f'ENTE\n')
            file.write(f'{authority_name}\n')
            file.write('======================================================================\n')
            file.write(f'VERIFICA ENTE\n')
            file.write(f'{is_on_agid_list}\n')
            file.write('======================================================================\n')

        report = Html2Pdf(folder, case_info, ntp)
        report.generate_pdf(True, info_file_path)
