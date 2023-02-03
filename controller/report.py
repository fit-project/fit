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

from fpdf import FPDF, Template
from common.report import ReportText
class Report:
    def __init__(self,acquisition_directory):
        self.acquisition_directory = acquisition_directory

    def generate_pdf(self,type,case_info,ntp):
        pdf = FPDF()
        phrases = ReportText()

        #FIRST PAGE
        version = "1.0"
        pdf.add_page()
        pdf.set_margins(32, 32, -1)

        pdf.add_font('Palatino', '', r'C:\Users\Routi\fit\asset\fonts\pala.ttf', uni=True)
        #margin w, margin h
        pdf.set_font("Palatino", size=32)
        pdf.cell(200, 10, txt=phrases.TEXT['title'], ln=2)
        pdf.set_font("Palatino", size=16)
        pdf.cell(200, 20, txt=phrases.TEXT['report'], ln=2)
        pdf.set_font("Palatino", size=14)
        pdf.cell(200, 20, txt='Versione: '+version, ln=2)
        pdf.multi_cell(190, 10, txt=phrases.TEXT['description'])


        pdf.set_font("Palatino", size=16)
        pdf.cell(200, 20, txt=phrases.TEXT['info'], ln=2)
        pdf.add_font('Palatino Bold', '', r'C:\Users\Routi\fit\asset\fonts\palab.ttf', uni=True)

        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[0], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['name'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['name'], ln=2)

        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[1], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['lawyer_name'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['lawyer_name'], ln=2)

        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[2], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['types_proceedings_id'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['types_proceedings_id'], ln=2)


        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[3], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['courthouse'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['courthouse'], ln=2)

        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[4], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['proceedings_number'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['proceedings_number'], ln=2)

        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[5], ln=2)
        pdf.set_font("Palatino", size=14)
        pdf.cell(200, 10, type, ln=2)

        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[6], ln=2)
        pdf.set_font("Palatino", size=14)
        pdf.cell(200, 10, str(ntp), ln=2)


        # save the pdf with name .pdf
        pdf.output(self.acquisition_directory+'_report.pdf')
        return
