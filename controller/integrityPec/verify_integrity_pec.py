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

from xhtml2pdf import pisa
from PyPDF2 import PdfMerger

from common.report import ReportText


class VerifyIntegrityPec:
    def __init__(self, cases_folder_path, case_info, ntp):
        self.cases_folder_path = cases_folder_path
        self.output_front = self.cases_folder_path + "\\" + "front_report.pdf"
        self.output_content = self.cases_folder_path + "\\" + "content_report.pdf"
        self.output_front_result = open(self.output_front, "w+b")
        self.output_content_result = open(self.output_content, "w+b")
        self.case_info = case_info
        self.ntp = ntp

    def generate_pdf(self, result, info_file_path):

        # PREPARING DATA TO FILL THE PDF
        phrases = ReportText()
        with open(info_file_path, "r") as f:
            info_file = f.read()
        # FILLING FRONT PAGE WITH DATA

        front_index = open(os.getcwd() + '/asset/templates/front.html').read().format(
            img=phrases.TEXT['img'], t1=phrases.TEXT['t1'],
            title=phrases.TEXT['title'], report=phrases.TEXT['verification'], version=phrases.TEXT['version']
        )

        if result:
            t3descr = phrases.TEXT['verifi_ok']
        else:
            t3descr = phrases.TEXT['verifi_ko']

        content_index = open(os.getcwd() + '/asset/templates/template_pec.html').read().format(

            title=phrases.TEXT['title'],
            index=phrases.TEXT['index'],
            description=phrases.TEXT['description'], t1=phrases.TEXT['t1'], t2=phrases.TEXT['t2'],
            case=phrases.TEXT['case'], casedata=phrases.TEXT['casedata'],
            case0=phrases.CASE[0], case1=phrases.CASE[1], case2=phrases.CASE[2],
            case3=phrases.CASE[3], case4=phrases.CASE[4], case5=phrases.CASE[5], case6=phrases.CASE[6],
            t3=phrases.TEXT['verification'], t3descr=t3descr,
            info_file=info_file,

            data0=str(self.case_info['name'] or 'N/A'),
            data1=str(self.case_info['lawyer_name'] or 'N/A'),
            data2=str(self.case_info['types_proceedings_id'] or 'N/A'),
            data3=str(self.case_info['courthouse'] or 'N/A'),
            data4=str(self.case_info['proceedings_number'] or 'N/A'),
            typed=phrases.TEXT['typed'], type=phrases.TEXT['verification'],
            date=phrases.TEXT['date'], ntp=self.ntp,

        )
        # create pdf front and content, merge them and remove merged files
        pisa.CreatePDF(front_index, dest=self.output_front_result)
        pisa.CreatePDF(content_index, dest=self.output_content_result)
        merger = PdfMerger()
        merger.append(self.output_front_result)
        merger.append(self.output_content_result)

        merger.write(self.cases_folder_path + "\\" + "report_integrity_pec_verification.pdf")
        merger.close()
        self.output_content_result.close()
        self.output_front_result.close()
        if os.path.exists(self.output_front):
            os.remove(self.output_front)
        if os.path.exists(self.output_content):
            os.remove(self.output_content)
        if os.path.exists(info_file_path):
            os.remove(info_file_path)

