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

from fpdf import FPDF
from common.report import ReportText


class Report:
    def __init__(self, cases_folder_path):
        self.cases_folder_path = cases_folder_path
        self.pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')

    def generate_pdf(self, type, case_info, ntp):

        phrases = ReportText()
        # add fonts (the only way to work with unicode characters)
        self.pdf.add_font('Palatino', '', os.getcwd() + '\\asset\\fonts\\pala.ttf', uni=True)
        self.pdf.add_font('Palatino Bold', '', os.getcwd() + '\\asset\\fonts\\palab.ttf', uni=True)
        self.pdf.add_font('Palatino Italic', '', os.getcwd() + '\\asset\\fonts\\palai.ttf', uni=True)

        # ------------------------ FRONT PAGE ------------------------
        self.pdf.add_page()
        self.pdf.set_xy(0, 0)
        self.pdf.set_left_margin(72 / 2)
        self.pdf.set_right_margin(72 / 2)
        self.pdf.image(os.getcwd() + '\\asset\\images\\FIT.png', x=40, y=20, w=0, h=0, type='PNG')
        # margin w, margin h

        self.pdf.set_xy(0, 120)
        self.pdf.set_font("Palatino", size=32)
        self.pdf.cell(200, 150, txt=phrases.TEXT['title'], ln=2, align='C')
        self.pdf.set_font("Palatino", size=16)
        self.pdf.cell(200, -100, txt=phrases.TEXT['report'], ln=2,align='C')
        # ------------------------ FIRST PAGE - FIT INFO ------------------------
        self.new_page()
        self.pdf.cell(200, 20, txt=phrases.TEXT['title'], ln=2)
        self.pdf.set_font("Palatino", size=14)
        self.pdf.multi_cell(190, 8, txt=phrases.TEXT['description'])


        # ------------------------  SECOND PAGE - CASE INFO ------------------------

        self.new_page()

        # client/case
        self.pdf.cell(200, 20, txt=phrases.TEXT['t1'], ln=2)
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[0], ln=2)
        self.pdf.set_font("Palatino", size=14)
        if case_info['name'] is None:
            self.pdf.cell(200, 5, 'N/A', ln=2)
        else:
            self.pdf.cell(200, 5, case_info['name'], ln=2)

        # lawyer
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[1], ln=2)
        self.pdf.set_font("Palatino", size=14)
        if case_info['lawyer_name'] is None:
            self.pdf.cell(200, 5, 'N/A', ln=2)
        else:
            self.pdf.cell(200, 5, case_info['lawyer_name'], ln=2)

        # type of proceeding
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[2], ln=2)
        self.pdf.set_font("Palatino", size=14)
        if case_info['types_proceedings_id'] is None:  # TODO: change in proceeding according to id
            self.pdf.cell(200, 5, 'N/A', ln=2)
        else:
            self.pdf.cell(200, 5, case_info['types_proceedings_id'], ln=2)

        # couthouse
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[3], ln=2)
        self.pdf.set_font("Palatino", size=14)
        if case_info['courthouse'] is None:
            self.pdf.cell(200, 5, 'N/A', ln=2)
        else:
            self.pdf.cell(200, 5, case_info['courthouse'], ln=2)

        # proceeding number
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[4], ln=2)
        self.pdf.set_font("Palatino", size=14)
        if case_info['proceedings_number'] is None:
            self.pdf.cell(200, 5, 'N/A', ln=2)
        else:
            self.pdf.cell(200, 5, case_info['proceedings_number'], ln=2)

        # type of acquisition
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[5], ln=2)
        self.pdf.set_font("Palatino", size=14)
        self.pdf.cell(200, 5, type, ln=2)

        # ntp
        self.pdf.set_font("Palatino Bold", size=14)
        self.pdf.cell(200, 20, phrases.CASE[6], ln=2)
        self.pdf.set_font("Palatino", size=14)
        self.pdf.cell(200, 5, str(ntp), ln=2)

        # ------------------------ THIRD PAGE - WHOIS INFORMATION ------------------------
        self.new_page()
        self.pdf.cell(200, 20, txt=phrases.TEXT['t2'], ln=2)

        self.pdf.set_font("Palatino", size=10)
        whois_text = open(self.cases_folder_path + "\\whois.txt", "r")
        text = ''
        for line in whois_text:
            text = text + line
        self.pdf.set_fill_color(220, 220, 220)
        self.pdf.multi_cell(0, 5, txt=str(text), fill=True, border=1)

        # THIRD PAGE - FILE PRODUCED FROM THE SYS
        self.new_page()
        self.pdf.cell(200, 20, txt=phrases.TEXT['t3'], ln=2)

        # get every file from the folder and write info
        self.pdf.set_font("Palatino", size=12)
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]
        for file in files:
            filename = os.path.join(self.cases_folder_path, file)
            extension = filename.partition('.')[2]
            self.pdf.cell(200, 10, txt=file + ": " + phrases.TEXT[extension], ln=2)

        # ------------------------ FOURTH PAGE - FILE PRODUCED FROM THE USER ------------------------
        self.new_page()
        self.pdf.cell(200, 20, txt=phrases.TEXT['t4'], ln=2)

        self.pdf.set_font("Palatino", size=12)
        hash_text = open(self.cases_folder_path + "\\acquisition.hash", "r")
        text = ''
        for line in hash_text:
            text = text + line
        self.pdf.set_fill_color(220, 220, 220)
        self.pdf.multi_cell(0, 5, txt=str(text), fill=True, border=1)

        # save the pdf
        self.pdf.output(
            self.cases_folder_path + "\\" + "acquisition_report.pdf")
        return

    def header(self):
        #implement footer
        return

    def new_page(self):
        #header
        self.pdf.add_page()

        self.pdf.set_left_margin(72 / 2)
        self.pdf.set_right_margin(72 / 2)

        self.pdf.set_font("Palatino", size=10)
        self.pdf.set_text_color(255,69,0) #orangered #ff4500 (255,69,0)
        self.pdf.cell(0, 5, 'Freezing Internet Tool', align='R')

        self.pdf.set_text_color(0,0,0) #black
        self.pdf.set_xy(10, 20)
        self.pdf.set_font("Palatino", size=16)
        return
