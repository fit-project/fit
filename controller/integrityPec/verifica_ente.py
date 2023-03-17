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
from bs4 import BeautifulSoup
from controller.integrityPec import revoca

# URL della prima pagina
url = 'https://www.agid.gov.it/it/piattaforme/posta-elettronica-certificata/elenco-gestori-pec'

def ver_ente():
    page_num = 0
    found = False
    ente = revoca.extract_ente()

    # Loop per scandire tutte le pagine
    while True:
        # Recupera la pagina web
        response = requests.get(f'{url}?page={page_num}')

        # Analizza il contenuto della pagina con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Verifica se la stringa ente è presente nella pagina
        if ente in soup.get_text():
            found = True

        # Verifica se ci sono altre pagine da analizzare
        next_button = soup.find('a', {'rel': 'next'})
        if next_button is None:
            break
        else:
            page_num += 1

    if not found:
        return -1
    else:
        return True