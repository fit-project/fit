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
from common.utility import get_logo, get_version, get_language

if get_language() == 'italian':
    import common.constants.controller.report as REPORT
else:
    import common.constants.controller.report_eng as REPORT




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
            img=get_logo(), t1=REPORT.T1,
            title=REPORT.TITLE, report=REPORT.REPORT, version=get_version()
        )

        # FILLING TEMPLATE WITH DATA
        if type == 'web':
            content_index_path = os.path.join("assets", "templates", "template_web.html")
            content_index = open(content_index_path).read().format(

                title=REPORT.TITLE,
                index=REPORT.INDEX,
                description=REPORT.DESCRIPTION, t1=REPORT.T1, t2=REPORT.T2,
                case=REPORT.CASEINFO, casedata=REPORT.CASEDATA,
                case0=REPORT.CASE, case1=REPORT.LAWYER, case2=REPORT.PROCEEDING,
                case3=REPORT.COURT, case4=REPORT.NUMBER, case5=REPORT.ACQUISITION_TYPE, case6=REPORT.ACQUISITION_DATE,

                data0=str(self.case_info['name'] or 'N/A'),
                data1=str(self.case_info['lawyer_name'] or 'N/A'),
                data2=str(self.case_info['proceeding_type'] or 'N/A'),
                data3=str(self.case_info['courthouse'] or 'N/A'),
                data4=str(self.case_info['proceeding_number'] or 'N/A'),
                typed=REPORT.TYPED, type=type,
                date=REPORT.DATE, ntp=ntp,
                t3=REPORT.T3, t3descr=REPORT.T3DESCR,
                whoisfile=whois_text,
                t4=REPORT.T4, t4descr=REPORT.T4DESCR,
                name=REPORT.NAME, descr=REPORT.DESCR,

                avi=acquisition_files[fnmatch.filter(acquisition_files.keys(), '*.avi')[0]], avid=REPORT.AVID,
                hash=acquisition_files['acquisition.hash'], hashd=REPORT.HASHD,
                log=acquisition_files['acquisition.log'], logd=REPORT.LOGD,
                pcap=acquisition_files['acquisition.pcap'], pcapd=REPORT.PCAPD,
                zip=acquisition_files[fnmatch.filter(acquisition_files.keys(), '*.zip')[0]], zipd=REPORT.ZIPD,
                whois=acquisition_files['whois.txt'], whoisd=REPORT.WHOISD,
                headers=acquisition_files['headers.txt'], headersd=REPORT.HEADERSD,
                nslookup=acquisition_files['nslookup.txt'], nslookupd=REPORT.PNGD,
                cer=acquisition_files['server.cer'], cerd=REPORT.CERD,
                sslkey=acquisition_files['sslkey.log'], sslkeyd=REPORT.SSLKEYD,
                traceroute=acquisition_files['traceroute.txt'], tracerouted=REPORT.TRACEROUTED,

                t5=REPORT.T5, t5descr=REPORT.T5DESCR, file=user_files,
                t6=REPORT.T6, t6descr=REPORT.T6DESCR, filedata=zip_enum,
                t7=REPORT.T7, t7descr=REPORT.T7DESCR,
                titlecc=REPORT.TITLECC, ccdescr=REPORT.CCDESCR,
                titleh=REPORT.TITLEH, hdescr=REPORT.HDESCR
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

        if type == 'email' or type == 'instagram' or type == 'youtube':
            content_index_path = os.path.join("assets", "templates",
                                              "template_email.html")
            content_index = open(content_index_path).read().format(

                title=REPORT.TITLE,
                index=REPORT.INDEX,
                description=REPORT.DESCRIPTION, t1=REPORT.T1, t2=REPORT.T2,
                case=REPORT.CASEINFO, casedata=REPORT.CASEDATA,
                case0=REPORT.CASE, case1=REPORT.LAWYER, case2=REPORT.PROCEEDING,
                case3=REPORT.COURT, case4=REPORT.NUMBER, case5=REPORT.ACQUISITION_TYPE, case6=REPORT.ACQUISITION_DATE,

                data0=str(self.case_info['name'] or 'N/A'),
                data1=str(self.case_info['lawyer_name'] or 'N/A'),
                data2=str(self.case_info['proceeding_type'] or 'N/A'),
                data3=str(self.case_info['courthouse'] or 'N/A'),
                data4=str(self.case_info['proceeding_number'] or 'N/A'),
                typed=REPORT.TYPED, type=type,
                date=REPORT.DATE, ntp=ntp,
                t4=REPORT.T4, t4descr=REPORT.T4DESCR,
                name=REPORT.NAME, descr=REPORT.DESCR,
                hash=acquisition_files['acquisition.hash'], hashd=REPORT.HASHD,
                log=acquisition_files['acquisition.log'], logd=REPORT.LOGD,
                zip=acquisition_files[fnmatch.filter(acquisition_files.keys(), '*.zip')[0]], zipd=REPORT.ZIPD,
                t5=REPORT.T5, t5descr=REPORT.T5DESCR, file=user_files,
                t6=REPORT.T6, t6descr=REPORT.T6DESCR, filedata=zip_enum,
                t7=REPORT.T7, t7descr=REPORT.T7DESCR,
                titlecc=REPORT.TITLECC, ccdescr=REPORT.CCDESCR,
                titleh=REPORT.TITLEH, hdescr=REPORT.HDESCR

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
            acquisition_files['acquisition.avi'] = REPORT.NOT_PRODUCED
        if not 'acquisition.hash' in acquisition_files.values():
            acquisition_files['acquisition.hash'] = REPORT.NOT_PRODUCED
        if not 'acquisition.log' in acquisition_files.values():
            acquisition_files['acquisition.log'] = REPORT.NOT_PRODUCED
        if not any(value.endswith('.pcap') for value in acquisition_files.values()):
            acquisition_files['acquisition.pcap'] = REPORT.NOT_PRODUCED
        if not any(value.endswith('.zip') for value in acquisition_files.values()):
            acquisition_files['acquisition.zip'] = REPORT.NOT_PRODUCED
        if not 'whois.txt' in acquisition_files.values():
            acquisition_files['whois.txt'] = REPORT.NOT_PRODUCED
        if not 'headers.txt' in acquisition_files.values():
            acquisition_files['headers.txt'] = REPORT.NOT_PRODUCED
        if not 'nslookup.txt' in acquisition_files.values():
            acquisition_files['nslookup.txt'] = REPORT.NOT_PRODUCED
        if not 'server.cer' in acquisition_files.values():
            acquisition_files['server.cer'] = REPORT.NOT_PRODUCED
        if not 'sslkey.log' in acquisition_files.values():
            acquisition_files['sslkey.log'] = REPORT.NOT_PRODUCED
        if not 'traceroute.txt' in acquisition_files.values():
            acquisition_files['traceroute.txt'] = REPORT.NOT_PRODUCED

        return acquisition_files

    def _zip_files_enum(self):
        zip_enum = ''
        zip_dir = ''
        # getting zip folder and passing file names and dimensions to the template
        for fname in os.listdir(self.cases_folder_path):
            if fname.endswith('.zip'):
                zip_dir = os.path.join(self.cases_folder_path , fname)

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
                zip_enum += '<p>'+REPORT.NOT_PRODUCED + str(size) + " bytes</p>"
                zip_enum += '<hr>'
        return zip_enum

    def __hash_reader(self):
        hash_text = ''
        with open(os.path.join(self.cases_folder_path, 'acquisition.hash'), "r", encoding='utf-8') as f:
            for line in f:
                hash_text += '<p>' + line + "</p>"
        return hash_text
