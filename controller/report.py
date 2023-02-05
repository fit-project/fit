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

from common.report import ReportText


class Report:
    def __init__(self, cases_folder_path,case_info):
        self.cases_folder_path = cases_folder_path
        self.output_file = self.cases_folder_path + "\\" + "acquisition_report.pdf"
        self.case_info = case_info

    def generate_pdf(self, type, ntp):
        self.result_file = open(self.output_file, "w+b")

        # PREPARING DATA TO FILL THE PDF
        new_case_info = self._data_check()  # check if data is not None
        phrases = ReportText()

        with open(self.cases_folder_path + "\\whois.txt", "r", encoding='utf-8') as f:
            whois_text = f.read()
            f.close()

        with open(self.cases_folder_path + "\\acquisition.hash", "r", encoding='utf-8') as f:
            user_files = f.read()
            f.close()

        extensions = self._extension_check()

        # FILLING TEMPLATE WITH DATA
        index = open(os.getcwd() + '/asset/templates/template.html').read().format(
            img=phrases.TEXT['img'],
            title=phrases.TEXT['title'], report=phrases.TEXT['report'], version=phrases.TEXT['version'],
            description=phrases.TEXT['description'], t1=phrases.TEXT['t1'],
            case=phrases.TEXT['case'], casedata=phrases.TEXT['casedata'],
            case0=phrases.CASE[0], case1=phrases.CASE[1], case2=phrases.CASE[2],
            case3=phrases.CASE[3], case4=phrases.CASE[4], case5=phrases.CASE[5], case6=phrases.CASE[6],

            data0=new_case_info[1], data1=new_case_info[2], data2=new_case_info[3],
            data3=new_case_info[4], data4=new_case_info[0],
            typed=phrases.TEXT['typed'], type=type,
            date=phrases.TEXT['date'], ntp=ntp,
            t2=phrases.TEXT['t2'], whois=whois_text, t3=phrases.TEXT['t3'],
            name=phrases.TEXT['name'], descr=phrases.TEXT['descr'],
            avi=extensions['avi'], avid=phrases.TEXT['avid'],
            hash=extensions['hash'], hashd=phrases.TEXT['hashd'],
            log=extensions['log'], logd=phrases.TEXT['logd'],
            pcap=extensions['pcap'], pcapd=phrases.TEXT['pcapd'],
            zip=extensions['zip'], zipd=phrases.TEXT['zipd'],
            txt=extensions['txt'], txtd=phrases.TEXT['txtd'],
            png=extensions['png'], pngd=phrases.TEXT['pngd'],
            t4=phrases.TEXT['t4'], file=user_files)

        pisa.CreatePDF(index, dest=self.result_file)
        self.result_file.close()

    def _extension_check(self):
        extensions = {}
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]
        for file in files:
            filename = os.path.join(self.cases_folder_path, file)
            extension = str(filename.partition('.')[2])
            extensions[extension] = str(file)
        if "png" not in extensions:
            extensions['png'] = "Screenshot non prodotto"  # todo: check errore cattura
        return extensions

    def _data_check(self):
        new_case_info = []
        for key in self.case_info:
            if self.case_info[key] is None:
                new_case_info.append('N/A')
            else:
                new_case_info.append(self.case_info[key])
        return new_case_info
