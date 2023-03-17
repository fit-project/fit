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

from common import utility
from PyQt5 import QtWidgets
from common.error import ErrorMessage

from view.configuration import Configuration as ConfigurationView
from controller.integrityPec.verify_integrity_pec import VerifyIntegrityPec as VerifyIntegrityPecController


class GenerateReport:
    def __init__(self):
        self.error_msg = ErrorMessage()
        return


    def generate_report_verification(self, mittente, destinatario, oggetto, data_invio, messaggio, data_scadenza,
                                     integrità, revoca, firma_digitale, today_date, ente, ver_ente, case_info,
                                     ntp, eml_file_path):


        caseIndex = oggetto.find("caso: ")
        caseSliceBefore = oggetto[:caseIndex]
        caseSliceAfter = oggetto[caseIndex:]
        oggetto = caseSliceBefore + "\n" + caseSliceAfter

        folder = os.path.dirname(eml_file_path)
        info_file_path = f'{folder}/pec_info.txt'
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(info_file_path, 'w') as file:
            file.write(f'DETTAGLI PEC:\n')
            file.write('======================================================================\n')
            file.write(f'MITTENTE\n')
            file.write(f'{mittente}\n')
            file.write('======================================================================\n')
            file.write(f'DESTINATARIO\n')
            file.write(f'{destinatario}\n')
            file.write('======================================================================\n')
            file.write(f'OGGETTO\n')
            file.write(f'{oggetto}\n')
            file.write('======================================================================\n')
            file.write(f'DATA INVIO\n')
            file.write(f'{data_invio}\n')
            file.write('======================================================================\n')
            file.write(f'\n')
            file.write(f'RISULTATI:\n')
            file.write('======================================================================\n')
            file.write(f'DATA SCADENZA\n')
            file.write(f'{data_scadenza}\n')
            file.write('======================================================================\n')
            file.write(f'FIRMA DIGITALE\n')
            file.write(f'{firma_digitale}\n')
            file.write('======================================================================\n')
            file.write(f'INTEGRITA''\n')
            file.write(f'{integrità}\n')
            file.write('======================================================================\n')
            file.write(f'CRL\n')
            file.write(f'{revoca}\n')
            file.write('======================================================================\n')
            file.write(f'ENTE\n')
            file.write(f'{ente}\n')
            file.write('======================================================================\n')
            file.write(f'VERIFICA ENTE\n')
            file.write(f'{ver_ente}\n')
            file.write('======================================================================\n')

        report = VerifyIntegrityPecController(folder, case_info, ntp)
        report.generate_pdf(True, info_file_path)
        return report, info_file_path
