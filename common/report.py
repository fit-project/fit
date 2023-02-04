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

class ReportText:
    def __init__(self):
        self.TEXT = {
            'title': "Freezing Internet Tool",
            'report': "Report Freezing Internet Tool",
            'description': "FIT - Freezing Internet Tool è un’applicazione per l'acquisizione forense di contenuti "
                           "come pagine web, e-mail e social media direttamente da internet.",
            't1': "Informazioni generali",
            't2' : "Verifica titolarità dei dati",
            't3': "File prodotti dal sistema",
            't4': "File prodotti dall'utente",

            'avi': "acquisizione video",
            'hash': "file contenente gli hash dei file",
            'log': "informazioni generate dai vari componenti del sistema",
            'pcap': "registrazione del traffico di rete",
            'zip': "archivio contenente l'acquisizione",
            'txt': "file whois",
            'png': "screenshot della pagina"

        }
        self.CASE = ["Cliente / Caso", "Avvocato","Tipo di procedimento",
                     "Tribunale","Numero di procedimento","Tipo di acquisizione","Data acquisizione"]
