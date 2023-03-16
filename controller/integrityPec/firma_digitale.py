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


# Carica l'email da un file
def firma_src(file_path):
    message_text = " "

    with open(file_path, "r") as f:
        msg = email.message_from_file(f)

    # Verifica se c'è una firma nell'email
    if msg.is_multipart():
        found = False
        for part in msg.get_payload():
            if part.get_content_type() == 'application/pkcs7-signature':
                found = True

        for part in msg.walk():
            # Se la parte è di tipo "text/plain" estrai il testo
            if part.get_content_type() == 'text/plain':
                if part.get_content_charset() == 'utf-8' or part.get_content_charset() == 'UTF-8':
                    message_text = part.get_payload(decode=True).decode('iso-8859-1')

    vettore = [found, message_text]
    return vettore
