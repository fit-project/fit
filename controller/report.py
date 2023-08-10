#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import base64
import fnmatch
import os

from xhtml2pdf import pisa
from PyPDF2 import PdfMerger
import zipfile

from controller.configurations.tabs.general.typesproceedings import (
    TypesProceedings as TypesProceedingsController,
)

from common.utility import get_logo, get_version, get_language
from model.case import Case


class Report:
    def __init__(self, cases_folder_path, case_info):
        self.cases_folder_path = cases_folder_path
        self.output_front = os.path.join(self.cases_folder_path, "front_report.pdf")
        self.output_content = os.path.join(self.cases_folder_path, "content_report.pdf")
        self.output_front_result = open(self.output_front, "w+b")
        self.output_content_result = open(self.output_content, "w+b")
        case = Case()
        self.case_info = vars(case.get_from_id(case_info["id"]))

        language = get_language()
        if language == "Italian":
            import common.constants.controller.report as REPORT
        else:
            import common.constants.controller.report_eng as REPORT
        self.REPORT = REPORT

    def generate_pdf(self, type, ntp):
        # PREPARING DATA TO FILL THE PDF
        if type == "web":
            try:
                with open(os.path.join(self.cases_folder_path, "whois.txt"), "r") as f:
                    whois_text = f.read()
                    f.close()
            except:
                whois_text = self.REPORT.NOT_PRODUCED
            if whois_text == "" or whois_text == "\n":
                whois_text = self.REPORT.NOT_PRODUCED

        hash_file_content = self.__hash_reader()
        screenshot = self.__insert_screenshot()
        video = self.__insert_video_hyperlink()

        proceeding_type = TypesProceedingsController().get_proceeding_name_by_id(
            self.case_info.get("proceeding_type", 0)
        )

        logo = self.case_info.get("logo_bin", "")
        if logo is not None:
            logo = (
                '<div style="padding-bottom: 10px;"><img src="data:image/png;base64,'
                + base64.b64encode(logo).decode("utf-8")
                + '" height="'
                + self.case_info.get("logo_height", "")
                + '" width="'
                + self.case_info.get("logo_width", "")
                + '"></div>'
            )
        else:
            logo = "<div></div>"

        acquisition_files = self._acquisition_files_names()

        zip_enum = self._zip_files_enum()

        # FILLING FRONT PAGE WITH DATA
        front_index_path = os.path.join("assets", "templates", "front.html")
        front_index = (
            open(front_index_path)
            .read()
            .format(
                img=get_logo(),
                t1=self.REPORT.T1,
                title=self.REPORT.TITLE,
                report=self.REPORT.REPORT,
                version=get_version(),
            )
        )

        # FILLING TEMPLATE WITH DATA
        if type == "web" and whois_text != self.REPORT.NOT_PRODUCED:
            content_index_path = os.path.join(
                "assets", "templates", "template_web.html"
            )
            content_index = (
                open(content_index_path)
                .read()
                .format(
                    title=self.REPORT.TITLE,
                    index=self.REPORT.INDEX,
                    description=self.REPORT.DESCRIPTION.format(
                        self.REPORT.RELEASES_LINK
                    ),
                    t1=self.REPORT.T1,
                    t2=self.REPORT.T2,
                    case=self.REPORT.CASEINFO,
                    casedata=self.REPORT.CASEDATA,
                    case0=self.REPORT.CASE,
                    case1=self.REPORT.LAWYER,
                    case2=self.REPORT.OPERATOR,
                    case3=self.REPORT.PROCEEDING,
                    case4=self.REPORT.COURT,
                    case5=self.REPORT.NUMBER,
                    case6=self.REPORT.ACQUISITION_TYPE,
                    case7=self.REPORT.ACQUISITION_DATE,
                    case8=self.REPORT.NOTES,
                    data0=str(self.case_info["name"] or "N/A"),
                    data1=str(self.case_info["lawyer_name"] or "N/A"),
                    data2=str(self.case_info["operator"] or "N/A"),
                    data3=proceeding_type,
                    data4=str(self.case_info["courthouse"] or "N/A"),
                    data5=str(self.case_info["proceeding_number"] or "N/A"),
                    data6=type,
                    data7=ntp,
                    data8=str(self.case_info["notes"] or "N/A").replace("\n", "<br>"),
                    t3=self.REPORT.T3,
                    t3descr=self.REPORT.T3DESCR,
                    whoisfile=whois_text,
                    t4=self.REPORT.T4,
                    t4descr=self.REPORT.T4DESCR,
                    name=self.REPORT.NAME,
                    descr=self.REPORT.DESCR,
                    avi=acquisition_files[
                        fnmatch.filter(acquisition_files.keys(), "*.avi")[0]
                    ],
                    avid=self.REPORT.AVID,
                    hash=acquisition_files["acquisition.hash"],
                    hashd=self.REPORT.HASHD,
                    log=acquisition_files["acquisition.log"],
                    logd=self.REPORT.LOGD,
                    pcap=acquisition_files["acquisition.pcap"],
                    pcapd=self.REPORT.PCAPD,
                    zip=acquisition_files[
                        fnmatch.filter(acquisition_files.keys(), "*.zip")[0]
                    ],
                    zipd=self.REPORT.ZIPD,
                    whois=acquisition_files["whois.txt"],
                    whoisd=self.REPORT.WHOISD,
                    headers=acquisition_files["headers.txt"],
                    headersd=self.REPORT.HEADERSD,
                    nslookup=acquisition_files["nslookup.txt"],
                    nslookupd=self.REPORT.NSLOOKUPD,
                    cer=acquisition_files["server.cer"],
                    cerd=self.REPORT.CERD,
                    sslkey=acquisition_files["sslkey.log"],
                    sslkeyd=self.REPORT.SSLKEYD,
                    traceroute=acquisition_files["traceroute.txt"],
                    tracerouted=self.REPORT.TRACEROUTED,
                    t5=self.REPORT.T5,
                    t5descr=self.REPORT.T5DESCR,
                    file=hash_file_content,
                    t6=self.REPORT.T6,
                    t6descr=self.REPORT.T6DESCR,
                    filedata=zip_enum,
                    t7=self.REPORT.T7,
                    t7descr=self.REPORT.T7DESCR,
                    screenshot=screenshot,
                    t8=self.REPORT.T8,
                    t8descr=self.REPORT.T8DESCR,
                    video_hyperlink=video,
                    t9=self.REPORT.T9,
                    t9descr=self.REPORT.T9DESCR,
                    titlecc=self.REPORT.TITLECC,
                    ccdescr=self.REPORT.CCDESCR,
                    titleh=self.REPORT.TITLEH,
                    hdescr=self.REPORT.HDESCR,
                    page=self.REPORT.PAGE,
                    of=self.REPORT.OF,
                    logo=logo,
                )
            )
            pdf_options = {
                "page-size": "Letter",
                "margin-top": "1in",
                "margin-right": "1in",
                "margin-bottom": "1in",
                "margin-left": "1in",
            }
            # create pdf front and content, merge them and remove merged files
            pisa.CreatePDF(
                front_index, dest=self.output_front_result, options=pdf_options
            )
            pisa.CreatePDF(
                content_index, dest=self.output_content_result, options=pdf_options
            )

        elif type == "web" and whois_text == self.REPORT.NOT_PRODUCED:
            content_index_path = os.path.join(
                "assets", "templates", "template_web_no_whois.html"
            )
            content_index = (
                open(content_index_path)
                .read()
                .format(
                    title=self.REPORT.TITLE,
                    index=self.REPORT.INDEX,
                    description=self.REPORT.DESCRIPTION.format(
                        self.REPORT.RELEASES_LINK
                    ),
                    t1=self.REPORT.T1,
                    t2=self.REPORT.T2,
                    case=self.REPORT.CASEINFO,
                    casedata=self.REPORT.CASEDATA,
                    case0=self.REPORT.CASE,
                    case1=self.REPORT.LAWYER,
                    case2=self.REPORT.OPERATOR,
                    case3=self.REPORT.PROCEEDING,
                    case4=self.REPORT.COURT,
                    case5=self.REPORT.NUMBER,
                    case6=self.REPORT.ACQUISITION_TYPE,
                    case7=self.REPORT.ACQUISITION_DATE,
                    case8=self.REPORT.NOTES,
                    data0=str(self.case_info["name"] or "N/A"),
                    data1=str(self.case_info["lawyer_name"] or "N/A"),
                    data2=str(self.case_info["operator"] or "N/A"),
                    data3=proceeding_type,
                    data4=str(self.case_info["courthouse"] or "N/A"),
                    data5=str(self.case_info["proceeding_number"] or "N/A"),
                    data6=type,
                    data7=ntp,
                    data8=str(self.case_info["notes"] or "N/A").replace("\n", "<br>"),
                    t4=self.REPORT.T4,
                    t4descr=self.REPORT.T4DESCR,
                    name=self.REPORT.NAME,
                    descr=self.REPORT.DESCR,
                    avi=acquisition_files[
                        fnmatch.filter(acquisition_files.keys(), "*.avi")[0]
                    ],
                    avid=self.REPORT.AVID,
                    hash=acquisition_files["acquisition.hash"],
                    hashd=self.REPORT.HASHD,
                    log=acquisition_files["acquisition.log"],
                    logd=self.REPORT.LOGD,
                    pcap=acquisition_files["acquisition.pcap"],
                    pcapd=self.REPORT.PCAPD,
                    zip=acquisition_files[
                        fnmatch.filter(acquisition_files.keys(), "*.zip")[0]
                    ],
                    zipd=self.REPORT.ZIPD,
                    whois=acquisition_files["whois.txt"],
                    whoisd=self.REPORT.WHOISD,
                    headers=acquisition_files["headers.txt"],
                    headersd=self.REPORT.HEADERSD,
                    nslookup=acquisition_files["nslookup.txt"],
                    nslookupd=self.REPORT.NSLOOKUPD,
                    cer=acquisition_files["server.cer"],
                    cerd=self.REPORT.CERD,
                    sslkey=acquisition_files["sslkey.log"],
                    sslkeyd=self.REPORT.SSLKEYD,
                    traceroute=acquisition_files["traceroute.txt"],
                    tracerouted=self.REPORT.TRACEROUTED,
                    t5=self.REPORT.T5,
                    t5descr=self.REPORT.T5DESCR,
                    file=hash_file_content,
                    t6=self.REPORT.T6,
                    t6descr=self.REPORT.T6DESCR,
                    filedata=zip_enum,
                    t7=self.REPORT.T7,
                    t7descr=self.REPORT.T7DESCR,
                    screenshot=screenshot,
                    t8=self.REPORT.T8,
                    t8descr=self.REPORT.T8DESCR,
                    video_hyperlink=video,
                    t9=self.REPORT.T9,
                    t9descr=self.REPORT.T9DESCR,
                    titlecc=self.REPORT.TITLECC,
                    ccdescr=self.REPORT.CCDESCR,
                    titleh=self.REPORT.TITLEH,
                    hdescr=self.REPORT.HDESCR,
                    page=self.REPORT.PAGE,
                    of=self.REPORT.OF,
                    logo=logo,
                )
            )

            pdf_options = {
                "page-size": "Letter",
                "margin-top": "1in",
                "margin-right": "1in",
                "margin-bottom": "1in",
                "margin-left": "1in",
            }
            # create pdf front and content, merge them and remove merged files
            pisa.CreatePDF(
                front_index, dest=self.output_front_result, options=pdf_options
            )
            pisa.CreatePDF(
                content_index, dest=self.output_content_result, options=pdf_options
            )

        if type == "email" or type == "instagram" or type == "video":
            content_index_path = os.path.join(
                "assets", "templates", "template_email.html"
            )
            content_index = (
                open(content_index_path)
                .read()
                .format(
                    title=self.REPORT.TITLE,
                    index=self.REPORT.INDEX,
                    description=self.REPORT.DESCRIPTION.format(
                        self.REPORT.RELEASES_LINK
                    ),
                    t1=self.REPORT.T1,
                    t2=self.REPORT.T2,
                    case=self.REPORT.CASEINFO,
                    casedata=self.REPORT.CASEDATA,
                    case0=self.REPORT.CASE,
                    case1=self.REPORT.LAWYER,
                    case2=self.REPORT.OPERATOR,
                    case3=self.REPORT.PROCEEDING,
                    case4=self.REPORT.COURT,
                    case5=self.REPORT.NUMBER,
                    case6=self.REPORT.ACQUISITION_TYPE,
                    case7=self.REPORT.ACQUISITION_DATE,
                    case8=self.REPORT.NOTES,
                    data0=str(self.case_info["name"] or "N/A"),
                    data1=str(self.case_info["lawyer_name"] or "N/A"),
                    data2=str(self.case_info["operator"] or "N/A"),
                    data3=proceeding_type,
                    data4=str(self.case_info["courthouse"] or "N/A"),
                    data5=str(self.case_info["proceeding_number"] or "N/A"),
                    data6=type,
                    data7=ntp,
                    data8=str(self.case_info["notes"] or "N/A").replace("\n", "<br>"),
                    t4=self.REPORT.T4,
                    t4descr=self.REPORT.T4DESCR,
                    name=self.REPORT.NAME,
                    descr=self.REPORT.DESCR,
                    hash=acquisition_files["acquisition.hash"],
                    hashd=self.REPORT.HASHD,
                    log=acquisition_files["acquisition.log"],
                    logd=self.REPORT.LOGD,
                    zip=acquisition_files[
                        fnmatch.filter(acquisition_files.keys(), "*.zip")[0]
                    ],
                    zipd=self.REPORT.ZIPD,
                    t5=self.REPORT.T5,
                    t5descr=self.REPORT.T5DESCR,
                    file=hash_file_content,
                    t6=self.REPORT.T6,
                    t6descr=self.REPORT.T6DESCR,
                    filedata=zip_enum,
                    t7=self.REPORT.T7,
                    t7descr=self.REPORT.T7DESCR,
                    titlecc=self.REPORT.TITLECC,
                    ccdescr=self.REPORT.CCDESCR,
                    titleh=self.REPORT.TITLEH,
                    hdescr=self.REPORT.HDESCR,
                    page=self.REPORT.PAGE,
                    of=self.REPORT.OF,
                    logo=logo,
                )
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

        if not any(value.endswith(".avi") for value in acquisition_files.values()):
            acquisition_files["acquisition.avi"] = self.REPORT.NOT_PRODUCED
        if not "acquisition.hash" in acquisition_files.values():
            acquisition_files["acquisition.hash"] = self.REPORT.NOT_PRODUCED
        if not "acquisition.log" in acquisition_files.values():
            acquisition_files["acquisition.log"] = self.REPORT.NOT_PRODUCED
        if not any(value.endswith(".pcap") for value in acquisition_files.values()):
            acquisition_files["acquisition.pcap"] = self.REPORT.NOT_PRODUCED
        if not any(value.endswith(".zip") for value in acquisition_files.values()):
            acquisition_files["acquisition.zip"] = self.REPORT.NOT_PRODUCED
        if not "whois.txt" in acquisition_files.values():
            acquisition_files["whois.txt"] = self.REPORT.NOT_PRODUCED
        if not "headers.txt" in acquisition_files.values():
            acquisition_files["headers.txt"] = self.REPORT.NOT_PRODUCED
        if not "nslookup.txt" in acquisition_files.values():
            acquisition_files["nslookup.txt"] = self.REPORT.NOT_PRODUCED
        if not "server.cer" in acquisition_files.values():
            acquisition_files["server.cer"] = self.REPORT.NOT_PRODUCED
        if not "sslkey.log" in acquisition_files.values():
            acquisition_files["sslkey.log"] = self.REPORT.NOT_PRODUCED
        if not "traceroute.txt" in acquisition_files.values():
            acquisition_files["traceroute.txt"] = self.REPORT.NOT_PRODUCED

        return acquisition_files

    def _zip_files_enum(self):
        zip_enum = ""
        zip_dir = ""
        # getting zip folder and passing file names and dimensions to the template
        for fname in os.listdir(self.cases_folder_path):
            if fname.endswith(".zip"):
                zip_dir = os.path.join(self.cases_folder_path, fname)

        zip_folder = zipfile.ZipFile(zip_dir)
        for zip_file in zip_folder.filelist:
            size = zip_file.file_size
            filename = zip_file.filename
            if filename.count(".") > 1:
                filename = filename.rsplit(".", 1)[0]
            else:
                pass
            if size > 0:
                zip_enum += "<p>" + filename + "</p>"
                zip_enum += "<p>" + self.REPORT.SIZE + str(size) + " bytes</p>"
                zip_enum += "<hr>"
        return zip_enum

    def __hash_reader(self):
        hash_text = ""
        with open(
            os.path.join(
                self.cases_folder_path,
                "acquisition.hash",
            ),
            "r",
            encoding="latin-1",
        ) as f:
            for line in f:
                hash_text += "<p>" + line + "</p>"
        return hash_text

    def __insert_screenshot(self):
        screenshot_text = ""
        screenshots_path = os.path.join(self.cases_folder_path, "screenshot")

        if os.path.isdir(screenshots_path):
            full_screenshot_path = os.path.join(
                self.cases_folder_path, "screenshot", "full_page"
            )
            main_screenshot_file = os.path.join(
                self.cases_folder_path, "screenshot.png"
            )

            url_folder = os.listdir(full_screenshot_path)
            full_screenshot_path = os.path.join(full_screenshot_path, url_folder[0])
            images = os.listdir(full_screenshot_path)
            main_screenshot = os.path.join(full_screenshot_path, images[0])
            print("test", main_screenshot)

            files = os.listdir(screenshots_path)
            for file in files:
                path = os.path.join(self.cases_folder_path, "screenshot", file)
                if os.path.isfile(path):
                    if "full_page_" not in os.path.basename(file):
                        screenshot_text += (
                            "<p>"
                            '<a href="file://'
                            + path
                            + '">'
                            + "Screenshot"
                            + os.path.basename(file)
                            + '</a><br><img src="'
                            + path
                            + '"></p><br><br>'
                        )

            # main full page screenshot
            screenshot_text += (
                "<p>"
                '<a href="file://'
                + main_screenshot_file
                + '">'
                + self.REPORT.COMPLETE_SCREENSHOT
                + '</a><br><img src="'
                + main_screenshot
                + '"></p>'
            )

        return screenshot_text

    def __insert_video_hyperlink(self):
        acquisition_files = {}
        files = [f.name for f in os.scandir(self.cases_folder_path) if f.is_file()]
        for file in files:
            acquisition_files[file] = file
        if not any(value.endswith(".avi") for value in acquisition_files.values()):
            hyperlink = self.REPORT.NOT_PRODUCED
        else:
            hyperlink = (
                '<a href="file://'
                + self.cases_folder_path
                + '">'
                + self.REPORT.VIDEO_LINK
                + "</a>"
            )
        return hyperlink
