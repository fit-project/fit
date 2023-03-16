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

from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
import os


def pdf_creator(mittente, destinatario, oggeto, data_invio, messaggio, data_scadenza, firma_digitale, integrita, revoca,
                ente, ver_ente, n):
    # Definisci il percorso dove trovare i template
    env = Environment(loader=FileSystemLoader('HTMLtoPDF'))


    # Carica il template HTML
    template = env.get_template('template.html')

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

    context = {
        'mittente': mittente,
        'destinatario': destinatario,
        'oggetto': oggeto,
        'data_invio': data_invio,
        'messaggio': messaggio,
        'data_scadenza': data_scadenza,
        'integrita': integrita,
        'revoca': revoca,
        'firma_digitale': firma_digitale,
        'today_date': today_date,
        'ente': ente,
        'ver_ente': ver_ente
    }

    # Renderizza il template HTML con il contesto e sostuisce le variabili {{}} con il loro valore
    html = template.render(context)

    # Genera il file PDF
    result = BytesIO()

    pisa_status = pisa.CreatePDF(html.encode('UTF-8'), dest=result)

    # Gestione errore
    if pisa_status.err:
        return 'Errore durante la generazione del PDF: %s' % pisa_status.err

    result.seek(0)

    # Salva il file PDF nella cartella "risultati"
    if not os.path.exists('risultati'):
        os.mkdir('risultati')

    if data_scadenza != "NULL":
        with open('Risultati/email_integra_' + str(n) + '.pdf', 'wb') as f:
            f.write(result.getvalue())
    else:
        with open('Risultati/email_alterata_' + str(n) + '.pdf', 'wb') as f:
            f.write(result.getvalue())
