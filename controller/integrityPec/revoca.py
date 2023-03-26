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

import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import re


# estrazione ente
def extract_ente():
    ente = False
    with open("certificato", "r") as fp:
        lines = fp.readlines()
        for row in lines:
            word = "Subject: "
            if row.find(word) != -1:
                if " O = " in row:
                    ente = row.split(" O = ")[1]
                    ente = ente.split(", ")[0]
                elif " O=" in row:
                    ente = row.split(" O=")[1]
                    ente = ente.split(", ")[0]
    return ente


# Estrazzione url certificato
def extract_url():
    with open("certificato", 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            word = 'URI:http'  # viene cercata la parola "Not After"
            if row.find(word) != -1:
                if "CRL" in row:
                    trovato = row
    if trovato:
        url = trovato.split("URI:")[1]
        # url = re.sub(r"\s{n}", "", url)
        url = url.strip()
        # url = str(url)
        return url
    else:
        return -1


# Analizza il file CRL
def analyze_CRL(crl_bytes, serial_number):
    crl = x509.load_der_x509_crl(crl_bytes, default_backend())
    found = False
    for revoked_cert in crl:
        if revoked_cert.serial_number == serial_number:
            found = True
            break

    if found == True:
        return True  # Il seriale è presente nell'elenco dei revocati
    else:
        return False  # Il seriale NON è presente nelll'elenci dei revocati


def revoca_der():
    url = extract_url()  # estre l'url

    response = requests.get(url)  # Effettua il download del file CRL

    crl_bytes = response.content  # Ottieni il contenuto del file CRL come stringa di byte

    crl_base64 = base64.b64encode(crl_bytes).decode('utf-8')  # Codifica il contenuto del file CRL in base64

    crl_bytes = base64.b64decode(crl_base64)  # codifica il contenuto in base64

    regex = r"\b([0-9a-fA-F]{2}:){15}[0-9a-fA-F]{2}\b"  # template del tipo di riga da cercare

    with open("certificato") as f:
        for line in f:
            match = re.search(regex, line)
            if match:
                serial_number = match.group()
                break

    found = analyze_CRL(crl_bytes, serial_number)

    if found:

        return found

    else:

        return found
