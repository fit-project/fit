#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os

from xhtml2pdf import pisa
from PyPDF2 import PdfMerger

from common.report import ReportText


class VerifyPDFTimestamp:
    def __init__(self, cases_folder_path, case_info, ntp):
        self.cases_folder_path = cases_folder_path
        self.output_front = os.path.join(self.cases_folder_path, "front_report.pdf")
        self.output_content = os.path.join(self.cases_folder_path, "content_report.pdf")
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
        front_html = os.path.join('assets/templates/front.html')
        front_index = open(front_html).read().format(
            img=phrases.TEXT['img'], t1=phrases.TEXT['t1'],
            title=phrases.TEXT['title'], report=phrases.TEXT['verification'], version=phrases.TEXT['version']
        )

        if result:
            t3descr = phrases.TEXT['verifi_ok']
        else:
            t3descr = phrases.TEXT['verifi_ko']

        content_html = os.path.join('assets/templates/template_verification.html')
        content_index = open(content_html).read().format(

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
            data2=str(self.case_info['proceeding_type'] or 'N/A'),
            data3=str(self.case_info['courthouse'] or 'N/A'),
            data4=str(self.case_info['proceeding_number'] or 'N/A'),
            typed=phrases.TEXT['typed'], type=phrases.TEXT['verification'],
            date=phrases.TEXT['date'], ntp=self.ntp,

        )
        # create pdf front and content, merge them and remove merged files
        pisa.CreatePDF(front_index, dest=self.output_front_result)
        pisa.CreatePDF(content_index, dest=self.output_content_result)
        merger = PdfMerger()
        merger.append(self.output_front_result)
        merger.append(self.output_content_result)

        report_html = os.path.join(self.cases_folder_path, "report_timestamp_verification.pdf")
        merger.write(report_html)
        merger.close()

        self.output_content_result.close()
        self.output_front_result.close()
        if os.path.exists(self.output_front):
            os.remove(self.output_front)
        if os.path.exists(self.output_content):
            os.remove(self.output_content)
        if os.path.exists(info_file_path):
            os.remove(info_file_path)