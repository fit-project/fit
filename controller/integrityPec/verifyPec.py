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
import hashlib
import os
import subprocess

import rfc3161ng

from common import utility
from view.error import Error as ErrorView
from PyQt5 import QtWidgets
from common.error import ErrorMessage
from controller.integrityPec import scadenza_pec
from controller.integrityPec import firma_digitale
from controller.integrityPec import revoca
from controller.integrityPec import verifica_ente
from controller.integrityPec.HTMLtoPDF import converter
from controller.integrityPec.verify_integrity_pec import VerifyIntegrityPec as VerifyIntegrityPecController

class verifyPec:
    def __init__(self):
        self.error_msg = ErrorMessage()
        return

    def verifyPec(self, path, case_info, ntp):
        eml_file_path = path


        ris_sca_pec = scadenza_pec.crt_extract(eml_file_path)  # -1 mail corrotta, TRUE mail inviata prima della scadenza, FALSE dopo la scadenza
        if ris_sca_pec != -1:
            # Verifica se è presente una firma digitale
            ris_firma = firma_digitale.firma_src(eml_file_path)  # TRUE la firma è presente, FALSE altrimenti
            # verifica se la pec è stata revocata
            ris_rev = revoca.revoca_der()
            ente = revoca.extract_ente()
            ver_ente = verifica_ente.ver_ente()
            converter.pdf_creator(
                ris_sca_pec[1],
                ris_sca_pec[2],
                ris_sca_pec[3],
                ris_sca_pec[4],
                ris_firma[1],
                ris_sca_pec[0],
                ris_firma[0],
                True,
                ris_rev,
                ente,
                ver_ente,
                1,
                case_info,
                ntp,
                eml_file_path)
        else:
            with open(eml_file_path, 'rb') as f:
                msg = email.message_from_binary_file(f)

            mittente = msg['Reply-To']
            destinatario = msg['To']
            oggetto = msg['Subject']
            data_invio = msg['Date']
            messaggio = ris_firma = firma_digitale.firma_src(eml_file_path)  # TRUE la firma è presente, FALSE altrimenti

            converter.pdf_creator(
                mittente,
                destinatario,
                oggetto,
                data_invio,
                messaggio[1],
                'NULL',
                'NULL',
                False,
                'NULL',
                'NULL',
                False,
                1,
                case_info,
                ntp,
                eml_file_path)
