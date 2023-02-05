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


class ReportText:
    def __init__(self):
        self.TEXT = {
            'img': '..\\asset\\images\\FIT.png',
            'title': "Freezing Internet Tool",
            'report': "Report Freezing Internet Tool",
            'version': "Versione 1.0 beta",
            'description': "FIT - Freezing Internet Tool è un’applicazione per l'acquisizione forense di contenuti "
                           "come pagine web, e-mail e social media direttamente da internet. <br><br>"
                           "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                           "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                           "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
                           "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
                           "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit "
                           "anim id est laborum <br>"
                           "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                           "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                           "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
                           "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
                           "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit "
                           "anim id est laborum",
            't1': "Informazioni generali",
            'case': "Informazioni sul caso",
            'casedata': "Dati sul caso",
            'typed':"Tipo di acquisizione",
            'date': "Data acquisizione",
            't2': "Verifica titolarità dei dati",
            't3': "File prodotti dal sistema",
            'name': "Nome del file",
            'descr': "Descrizione",
            'avid': "acquisizione video",
            'hashd': "file contenente gli hash dei file",
            'logd': "informazioni generate dai vari componenti del sistema",
            'pcapd': "registrazione del traffico di rete",
            'zipd': "archivio contenente l'acquisizione",
            'txtd': "file whois",
            'pngd': "screenshot della pagina",
            't4': "File prodotti dall'utente"

        }
        self.CASE = ["Cliente / Caso", "Avvocato", "Tipo di procedimento",
                     "Tribunale", "Numero di procedimento", "Tipo di acquisizione", "Data acquisizione"]
