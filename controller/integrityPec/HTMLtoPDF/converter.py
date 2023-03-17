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

from datetime import datetime
from controller.integrityPec.generateReport import GenerateReport as GenerateReportController



def pdf_creator(mittente, destinatario, oggetto, data_invio, messaggio, data_scadenza, firma_digitale, integrita, revoca,
                ente, ver_ente, n, case_info):

    # Definisce il contesto per il template HTML
    if firma_digitale == True:
        firma_digitale = "Il messaggio presenta una firma digitale."
    else:
        firma_digitale = "Il messaggio non presenta una firma digitale."

    if integrita == True:
        integrita = "Il messaggio non e' stato alterato."
    else:
        integrita = "Il messaggio e' stato alterato."

    if ver_ente == True:
        ver_ente = 'L\'ente e\' presente nell elenco dei gestori pec certificiati Agid'
    else:
        ver_ente = 'L\'ente non e\' presente nell elenco dei gestori per certificati Agid'

    if revoca == True:
        revoca = "L'indirizzo usato per inviare il messaggio e' stato revocato."
    else:
        revoca = "L'indirizzo non e' stato revocato."

    today_date = datetime.today().strftime("%d %b, %Y")

    verifyPec = GenerateReportController()
    verifyPec.generate_report_verification(mittente, destinatario, oggetto, data_invio, messaggio, data_scadenza,
                                           integrita, revoca, firma_digitale, today_date, ente, ver_ente, case_info)

