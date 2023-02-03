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
    def __init__(self,cases_folder_path):
        self.cases_folder_path = cases_folder_path

    def generate_pdf(self,type,case_info,ntp):
        pdf = FPDF()
        phrases = ReportText()

        #FIRST PAGE - FRONTPAGE
        pdf.add_page()
        pdf.set_xy(10, 20)

        #add fonts (the only way to work with unicode chraacters)
        pdf.add_font('Palatino', '', os.getcwd()+'\\asset\\fonts\\pala.ttf', uni=True)
        pdf.add_font('Palatino Bold', '', os.getcwd()+'\\asset\\fonts\\palab.ttf', uni=True)

        #margin w, margin h
        pdf.set_font("Palatino", size=32)
        pdf.cell(200, 10, txt=phrases.TEXT['title'], ln=2)
        pdf.set_font("Palatino", size=16)
        pdf.cell(200, 20, txt=phrases.TEXT['report'], ln=2)
        pdf.set_font("Palatino", size=14)
        pdf.cell(200, 20, txt=phrases.TEXT['version'], ln=2)
        pdf.multi_cell(190, 10, txt=phrases.TEXT['description'])

        # SECOND PAGE - CASE INFO
        pdf.add_page()
        pdf.set_xy(10, 20)
        pdf.set_font("Palatino", size=16)
        pdf.cell(200, 20, txt=phrases.TEXT['t1'], ln=2)

        # client/case
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 10, phrases.CASE[0], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['name'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['name'], ln=2)

        # lawyer
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[1], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['lawyer_name'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['lawyer_name'], ln=2)

        # type of proceeding
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[2], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['types_proceedings_id'] is None: #TODO: change in proceeding according to id
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['types_proceedings_id'], ln=2)

        # couthouse
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[3], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['courthouse'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['courthouse'], ln=2)

        # proceeding number
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[4], ln=2)
        pdf.set_font("Palatino", size=14)
        if case_info['proceedings_number'] is None:
            pdf.cell(200, 10, 'N/A', ln=2)
        else:
            pdf.cell(200, 10, case_info['proceedings_number'], ln=2)

        # type of acquisition
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[5], ln=2)
        pdf.set_font("Palatino", size=14)
        pdf.cell(200, 10, type, ln=2)

        # ntp
        pdf.set_font("Palatino Bold", size=14)
        pdf.cell(200, 20, phrases.CASE[6], ln=2)
        pdf.set_font("Palatino", size=14)
        pdf.cell(200, 10, str(ntp), ln=2)


        # THIRD PAGE - WHOIS INFORMATION
        pdf.add_page()
        pdf.set_xy(10, 20)

        pdf.set_font("Palatino", size=16)
        pdf.cell(200, 20, txt=phrases.TEXT['t2'], ln=2)

        pdf.set_font("Palatino", size=12)
        whois_text = open(self.cases_folder_path+"\\whois.txt", "r")
        text= ''
        for line in whois_text:
            text = text+line
        pdf.set_fill_color(220,220,220)
        pdf.multi_cell(0, 5, txt=str(text), fill=True, border=1)

        # THIRD PAGE - FILE PRODUCED FROM THE SYS
        pdf.add_page()
        pdf.set_xy(10, 20)

        pdf.set_font("Palatino", size=16)
        pdf.cell(200, 20, txt=phrases.TEXT['t3'], ln=2)

        # get every file from the folder and write info
        pdf.set_font("Palatino", size=12)
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]
        for file in files:
            filename = os.path.join(self.cases_folder_path, file)
            extension = filename.partition('.')[2]
            pdf.cell(200, 10, txt=file+": "+phrases.TEXT[extension], ln=2)







        # save the pdf
        pdf.output(self.cases_folder_path+"\\"+case_info['name']+"_report.pdf") #TODO: check for correct file name
        return

    def get_files(self):
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]

        for file in files:
            filename = os.path.join(self.cases_folder_path, file)
            print(filename)
            extension = filename.partition('.')[2]



