#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import fnmatch
import os

from xhtml2pdf import pisa
from PyPDF2 import PdfMerger
import zipfile

from common.report import ReportText


class Report:
    def __init__(self, cases_folder_path, case_info):
        self.cases_folder_path = cases_folder_path
        self.output_front = os.path.join(self.cases_folder_path, "front_report.pdf")
        self.output_content = os.path.join(self.cases_folder_path, "content_report.pdf")
        self.output_front_result = open(self.output_front, "w+b")
        self.output_content_result = open(self.output_content, "w+b")
        self.case_info = case_info

    def generate_pdf(self, type, ntp):

        # PREPARING DATA TO FILL THE PDF
        phrases = ReportText()
        if type == 'web':
            try:
                with open(os.path.join(self.cases_folder_path, 'whois.txt'), "r") as f:
                    whois_text = f.read()
                    f.close()
            except:
                whois_text = 'Not produced'

        user_files = self.__hash_reader()

        acquisition_files = self._acquisition_files_names()

        zip_enum = self._zip_files_enum()

        # FILLING FRONT PAGE WITH DATA
        front_index_path = os.path.join("assets", "templates","front.html")
        front_index = open(front_index_path).read().format(
            img=phrases.TEXT['img'], t1=phrases.TEXT['t1'],
            title=phrases.TEXT['title'], report=phrases.TEXT['report'], version=phrases.TEXT['version']
        )

        # FILLING TEMPLATE WITH DATA
        if type == 'web':
            content_index_path = os.path.join("assets", "templates", "template_web.html")
            content_index = open(content_index_path).read().format(

                title=phrases.TEXT['title'],
                index=phrases.TEXT['index'],
                description=phrases.TEXT['description'], t1=phrases.TEXT['t1'], t2=phrases.TEXT['t2'],
                case=phrases.TEXT['case'], casedata=phrases.TEXT['casedata'],
                case0=phrases.CASE[0], case1=phrases.CASE[1], case2=phrases.CASE[2],
                case3=phrases.CASE[3], case4=phrases.CASE[4], case5=phrases.CASE[5], case6=phrases.CASE[6],

                data0=str(self.case_info['name'] or 'N/A'),
                data1=str(self.case_info['lawyer_name'] or 'N/A'),
                data2=str(self.case_info['proceeding_type'] or 'N/A'),
                data3=str(self.case_info['courthouse'] or 'N/A'),
                data4=str(self.case_info['proceeding_number'] or 'N/A'),
                typed=phrases.TEXT['typed'], type=type,
                date=phrases.TEXT['date'], ntp=ntp,
                t3=phrases.TEXT['t3'], t3descr=phrases.TEXT['t3descr'],
                whoisfile=whois_text,
                t4=phrases.TEXT['t4'], t4descr=phrases.TEXT['t4descr'],
                name=phrases.TEXT['name'], descr=phrases.TEXT['descr'],

                avi=acquisition_files[fnmatch.filter(acquisition_files.keys(), '*.avi')[0]], avid=phrases.TEXT['avid'],
                hash=acquisition_files['acquisition.hash'], hashd=phrases.TEXT['hashd'],
                log=acquisition_files['acquisition.log'], logd=phrases.TEXT['logd'],
                pcap=acquisition_files['acquisition.pcap'], pcapd=phrases.TEXT['pcapd'],
                zip=acquisition_files[fnmatch.filter(acquisition_files.keys(), '*.zip')[0]], zipd=phrases.TEXT['zipd'],
                whois=acquisition_files['whois.txt'], whoisd=phrases.TEXT['whoisd'],
                headers=acquisition_files['headers.txt'], headersd=phrases.TEXT['headersd'],
                nslookup=acquisition_files['nslookup.txt'], nslookupd=phrases.TEXT['pngd'],
                cer=acquisition_files['server.cer'], cerd=phrases.TEXT['cerd'],
                sslkey=acquisition_files['sslkey.log'], sslkeyd=phrases.TEXT['sslkeyd'],
                traceroute=acquisition_files['traceroute.txt'], tracerouted=phrases.TEXT['tracerouted'],

                t5=phrases.TEXT['t5'], t5descr=phrases.TEXT['t5descr'], file=user_files,
                t6=phrases.TEXT['t6'], t6descr=phrases.TEXT['t6descr'], filedata=zip_enum,
                t7=phrases.TEXT['t7'], t7descr=phrases.TEXT['t7descr'],
                titlecc=phrases.TEXT['titlecc'], ccdescr=phrases.TEXT['ccdescr'],
                titleh=phrases.TEXT['titleh'], hdescr=phrases.TEXT['hdescr']
            )
            pdf_options = {
                'page-size': 'Letter',
                'margin-top': '1in',
                'margin-right': '1in',
                'margin-bottom': '1in',
                'margin-left': '1in',
            }
            # create pdf front and content, merge them and remove merged files
            pisa.CreatePDF(front_index, dest=self.output_front_result, options=pdf_options)
            pisa.CreatePDF(content_index, dest=self.output_content_result, options=pdf_options)

        if type == 'email' or type == 'instagram' or type == 'video':
            content_index_path = os.path.join("assets", "templates",
                                              "template_email.html")
            content_index = open(content_index_path).read().format(

                title=phrases.TEXT['title'],
                index=phrases.TEXT['index'],
                description=phrases.TEXT['description'], t1=phrases.TEXT['t1'], t2=phrases.TEXT['t2'],
                case=phrases.TEXT['case'], casedata=phrases.TEXT['casedata'],
                case0=phrases.CASE[0], case1=phrases.CASE[1], case2=phrases.CASE[2],
                case3=phrases.CASE[3], case4=phrases.CASE[4], case5=phrases.CASE[5], case6=phrases.CASE[6],

                data0=str(self.case_info['name'] or 'N/A'),
                data1=str(self.case_info['lawyer_name'] or 'N/A'),
                data2=str(self.case_info['proceeding_type'] or 'N/A'),
                data3=str(self.case_info['courthouse'] or 'N/A'),
                data4=str(self.case_info['proceeding_number'] or 'N/A'),
                typed=phrases.TEXT['typed'], type=type,
                date=phrases.TEXT['date'], ntp=ntp,
                t4=phrases.TEXT['t4'], t4descr=phrases.TEXT['t4descr'],
                name=phrases.TEXT['name'], descr=phrases.TEXT['descr'],
                hash=acquisition_files['acquisition.hash'], hashd=phrases.TEXT['hashd'],
                log=acquisition_files['acquisition.log'], logd=phrases.TEXT['logd'],
                zip=acquisition_files[fnmatch.filter(acquisition_files.keys(), '*.zip')[0]], zipd=phrases.TEXT['zipd'],
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

        merger.write(os.path.join(self.cases_folder_path, "acquisition_report.pdf"))
        merger.close()
        self.output_content_result.close()
        self.output_front_result.close()
        if os.path.exists(self.output_front):
            os.remove(self.output_front)
        if os.path.exists(self.output_content):
            os.remove(self.output_content)


    def _acquisition_files_names(self):
        acquisition_files = {}
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]
        for file in files:
            acquisition_files[file] = file

        if not any(value.endswith('.avi') for value in acquisition_files.values()):
            acquisition_files['acquisition.avi'] = "File non prodotto"
        if not 'acquisition.hash' in acquisition_files.values():
            acquisition_files['acquisition.hash'] = "File non prodotto"
        if not 'acquisition.log' in acquisition_files.values():
            acquisition_files['acquisition.log'] = "File non prodotto"
        if not any(value.endswith('.pcap') for value in acquisition_files.values()):
            acquisition_files['acquisition.pcap'] = "File non prodotto"
        if not any(value.endswith('.zip') for value in acquisition_files.values()):
            acquisition_files['acquisition.zip'] = "File non prodotto"
        if not 'whois.txt' in acquisition_files.values():
            acquisition_files['whois.txt'] = "File non prodotto"
        if not 'headers.txt' in acquisition_files.values():
            acquisition_files['headers.txt'] = "File non prodotto"
        if not 'nslookup.txt' in acquisition_files.values():
            acquisition_files['nslookup.txt'] = "File non prodotto"
        if not 'server.cer' in acquisition_files.values():
            acquisition_files['server.cer'] = "File non prodotto"
        if not 'sslkey.log' in acquisition_files.values():
            acquisition_files['sslkey.log'] = "File non prodotto"
        if not 'traceroute.txt' in acquisition_files.values():
            acquisition_files['traceroute.txt'] = "File non prodotto"

        return acquisition_files

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
            if filename.count(".") > 1:
                filename = filename.rsplit(".", 1)[0]
            else:
                pass
            if size > 0:
                zip_enum += '<p>' + filename + "</p>"
                zip_enum += '<p>Dimensione: ' + str(size) + " bytes</p>"
                zip_enum += '<hr>'
        return zip_enum

    def __hash_reader(self):
        hash_text = ''
        with open(os.path.join(self.cases_folder_path, 'acquisition.hash', ), "r", encoding='latin-1') as f:
            for line in f:
                hash_text += '<p>' + line + "</p>"
        return hash_text
