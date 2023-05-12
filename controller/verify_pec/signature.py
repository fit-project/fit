#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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
