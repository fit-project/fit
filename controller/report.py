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
import zipfile

from common.report import ReportText


class Report:
    def __init__(self, cases_folder_path, case_info):
        self.cases_folder_path = cases_folder_path
        self.output_front = self.cases_folder_path + "\\" + "front_report.pdf"
        self.output_content = self.cases_folder_path + "\\" + "content_report.pdf"
        self.output_front_result = open(self.output_front, "w+b")
        self.output_content_result = open(self.output_content, "w+b")
        self.case_info = case_info

    def generate_pdf(self, type, ntp):

        # PREPARING DATA TO FILL THE PDF
        phrases = ReportText()
        if type == 'web':
            with open(self.cases_folder_path + "\\whois.txt", "r") as f:
                whois_text = f.read()
                f.close()
        with open(self.cases_folder_path + "\\acquisition.hash", "r", encoding='utf-8') as f:
            user_files = f.read()
            f.close()

        extensions = self._extension_check()

        zip_enum = self._zip_files_enum()

        # FILLING FRONT PAGE WITH DATA
        front_index = open(os.getcwd() + '/asset/templates/front.html').read().format(
            img=phrases.TEXT['img'], t1=phrases.TEXT['t1'],
            title=phrases.TEXT['title'], report=phrases.TEXT['report'], version=phrases.TEXT['version']
        )

        # FILLING TEMPLATE WITH DATA
        if type == 'web':
            content_index = open(os.getcwd() + '/asset/templates/template_web.html').read().format(

                title=phrases.TEXT['title'],
                index=phrases.TEXT['index'],
                description=phrases.TEXT['description'], t1=phrases.TEXT['t1'], t2=phrases.TEXT['t2'],
                case=phrases.TEXT['case'], casedata=phrases.TEXT['casedata'],
                case0=phrases.CASE[0], case1=phrases.CASE[1], case2=phrases.CASE[2],
                case3=phrases.CASE[3], case4=phrases.CASE[4], case5=phrases.CASE[5], case6=phrases.CASE[6],

                data0=str(self.case_info['name'] or 'N/A'),
                data1=str(self.case_info['lawyer_name'] or 'N/A'),
                data2=str(self.case_info['types_proceedings_id'] or 'N/A'),
                data3=str(self.case_info['courthouse'] or 'N/A'),
                data4=str(self.case_info['proceedings_number'] or 'N/A'),
                typed=phrases.TEXT['typed'], type=type,
                date=phrases.TEXT['date'], ntp=ntp,
                t3=phrases.TEXT['t3'], t3descr=phrases.TEXT['t3descr'],
                whois=whois_text,
                t4=phrases.TEXT['t4'], t4descr=phrases.TEXT['t4descr'],
                name=phrases.TEXT['name'], descr=phrases.TEXT['descr'],
                avi=extensions['avi'], avid=phrases.TEXT['avid'],
                hash=extensions['hash'], hashd=phrases.TEXT['hashd'],
                log=extensions['log'], logd=phrases.TEXT['logd'],
                pcap=extensions['pcap'], pcapd=phrases.TEXT['pcapd'],
                zip=extensions['zip'], zipd=phrases.TEXT['zipd'],
                txt=extensions['txt'], txtd=phrases.TEXT['txtd'],
                png=extensions['png'], pngd=phrases.TEXT['pngd'],
                t5=phrases.TEXT['t5'], t5descr=phrases.TEXT['t5descr'], file=user_files,
                t6=phrases.TEXT['t6'], t6descr=phrases.TEXT['t6descr'], filedata=zip_enum,
                t7=phrases.TEXT['t7'], t7descr=phrases.TEXT['t7descr'],
                titlecc=phrases.TEXT['titlecc'], ccdescr=phrases.TEXT['ccdescr'],
                titleh=phrases.TEXT['titleh'], hdescr=phrases.TEXT['hdescr']
            )
            # create pdf front and content, merge them and remove merged files
            pisa.CreatePDF(front_index, dest=self.output_front_result)
            pisa.CreatePDF(content_index, dest=self.output_content_result)


        if type == 'email':
            content_index = open(os.getcwd() + '/asset/templates/template_email.html').read().format(

                title=phrases.TEXT['title'],
                index=phrases.TEXT['index'],
                description=phrases.TEXT['description'], t1=phrases.TEXT['t1'], t2=phrases.TEXT['t2'],
                case=phrases.TEXT['case'], casedata=phrases.TEXT['casedata'],
                case0=phrases.CASE[0], case1=phrases.CASE[1], case2=phrases.CASE[2],
                case3=phrases.CASE[3], case4=phrases.CASE[4], case5=phrases.CASE[5], case6=phrases.CASE[6],

                data0=str(self.case_info['name'] or 'N/A'),
                data1=str(self.case_info['lawyer_name'] or 'N/A'),
                data2=str(self.case_info['types_proceedings_id'] or 'N/A'),
                data3=str(self.case_info['courthouse'] or 'N/A'),
                data4=str(self.case_info['proceedings_number'] or 'N/A'),
                typed=phrases.TEXT['typed'], type=type,
                date=phrases.TEXT['date'], ntp=ntp,
                t4=phrases.TEXT['t4'], t4descr=phrases.TEXT['t4descr'],
                name=phrases.TEXT['name'], descr=phrases.TEXT['descr'],
                hash=extensions['hash'], hashd=phrases.TEXT['hashd'],
                log=extensions['log'], logd=phrases.TEXT['logd'],
                zip=extensions['zip'], zipd=phrases.TEXT['zipd'],
                t5=phrases.TEXT['t5'], t5descr=phrases.TEXT['t5descr'], file=user_files,
                t6=phrases.TEXT['t6'], t6descr=phrases.TEXT['t6descr'], filedata=zip_enum,
                t7=phrases.TEXT['t7'], t7descr=phrases.TEXT['t7descr'],
                titlecc=phrases.TEXT['titlecc'], ccdescr=phrases.TEXT['ccdescr'],
                titleh=phrases.TEXT['titleh'], hdescr=phrases.TEXT['hdescr']

            )
            # create pdf front and content, merge them and remove merged files
            pisa.CreatePDF(front_index, dest=self.output_front_result)
            pisa.CreatePDF(content_index, dest=self.output_content_result)

        merger = PdfMerger()
        merger.append(self.output_front_result)
        merger.append(self.output_content_result)

        merger.write(self.cases_folder_path + "\\" + "acquisition_report.pdf")
        merger.close()
        self.output_content_result.close()
        self.output_front_result.close()
        if os.path.exists(self.output_front):
            os.remove(self.output_front)
        if os.path.exists(self.output_content):
            os.remove(self.output_content)

    def _extension_check(self):
        extensions = {}
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]
        for file in files:
            filename = os.path.join(self.cases_folder_path, file)
            extension = str(filename.partition('.')[2])
            extensions[extension] = str(file)
        if "png" not in extensions:
            extensions['png'] = "Screenshot non prodotto"  # todo: check problema cattura
        return extensions

    def _zip_files_enum(self):
        zip_enum = ''
        zip_dir = ''
        # getting zip folder and passing file names and dimensions to the template
        for fname in os.listdir(self.cases_folder_path):
            if fname.endswith('.zip'):
                zip_dir = self.cases_folder_path + "\\" + fname

        zip_folder = zipfile.ZipFile(zip_dir)
        for zip_file in zip_folder.filelist:
            size = zip_file.file_size
            filename = zip_file.filename
            if size > 0:
                zip_enum += '<p>' + filename + "</p>"
                zip_enum += '<p>Dimensione: ' + str(size) + " bytes</p>"
                zip_enum += '<hr>'
        return zip_enum
