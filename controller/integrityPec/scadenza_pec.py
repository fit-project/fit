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

from email import policy
from email.parser import BytesParser
from datetime import datetime
import subprocess
import os


def crt_extract(filePath):
    # estrazione certificato

    result = subprocess.run(
        ["openssl", "smime", "-verify", "-in", filePath, "-noverify", "-signer", "cert.pem", "-out", "textdata"],
        capture_output=True, text=True)

    # prelevare l'ente ceh ha estratto il certificato
    if result.returncode == 0:
        output = result.stdout
        os.system('openssl x509 -in cert.pem -text > certificato')
        return analyze_date(filePath)
        # fai qualcosa con l'output
    else:
        output = result.stderr
        return -1
        # gestisci l'errore
    # certificato decifrato


def analyze_date(filePath):
    # se il terminale risposnde con esito positivo allora si procede con l'estrazione delle 2 date
    file_path = 'certificato'

    with open(file_path, 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            word = 'Not After'  # viene cercata la parola "Not After"
            if row.find(word) != -1:
                date_s = row  # se viene trovata viene presa l'intera riga

    with open(filePath, 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)  # va a prendere tutte i metadata del file.eml

    # data scadenza
    date_s = date_s.split(" : ")[1]
    date_s = date_s.split(" G")[0]

    # Converte in timestamp la data passata come input
    date_s = datetime.strptime(date_s, '%b %d %I:%S:%M %Y')

    # Estrae mittente, destinatario e oggetto del messaggio
    mittente = msg['Reply-To']
    destinatario = msg['To']
    oggetto = msg['Subject']
    data_invio = msg['Date']

    vettore = [date_s, mittente, destinatario, oggetto, data_invio]
    return vettore


