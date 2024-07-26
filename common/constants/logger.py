#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

ACQUISITION_STARTED = "Acquisition started"
ACQUISITION_STOPPED = "Acquisition stopped"
ACQUISITION_FINISHED = "Acquisition finished"
NTP_ACQUISITION_TIME = "NTP {} acquisition time: {}"

# INFINITE LOOP
NETWORK_PACKET_CAPTURE_STARTED = "Network packet capture started"
NETWORK_PACKET_CAPTURE_STOPPED = "Network packet capture stopped"
NETWORK_PACKET_CAPTURE_COMPLETED = "Network packet capture completed"
SCREEN_RECODER_STARTED = "Screen recoder capture started"
SCREEN_RECODER_STOPPED = "Screen recoder capture stopped"
SCREEN_RECODER_COMPLETED = "Screen recoder capture completed"

# NETTOOLS
NSLOOKUP_GET_INFO_URL = "Get NSLOOKUP info for URL: {}"
NSLOOKUP_STARTED = "NSLOOKUP started"
NSLOOKUP_COMPLETED = "NSLOOKUP completed"

HEADERS_STARTED = "HEADERS started"
HEADERS_COMPLETED = "HEADERS completed"
HEADERS_GET_INFO_URL = "Get HEADERS info for URL: {}"

TRACEROUTE_STARTED = "TRACEROUTE started"
TRACEROUTE_COMPLETED = "TRACEROUTE completed"
TRACEROUTE_GET_INFO_URL = "Get TRACEROUTE info for URL: {}"

WHOIS_STARTED = "WHOIS started"
WHOIS_COMPLETED = "WHOIS completed"
WHOIS_GET_INFO_URL = "Get WHOIS info for URL: {}"

SSLKEYLOG_STARTED = "SSLKEYLOG started"
SSLKEYLOG_COMPLETED = "SSLKEYLOG completed"
SSLKEYLOG_GET = "Get SSLKEYLOG"

SSLCERTIFICATE_STARTED = "SSLCERTIFICATE started"
SSLCERTIFICATE_COMPLETED = "SSLCERTIFICATE completed"
SSLCERTIFICATE_GET_FROM_URL = "Get SSL certificate from URL: {}"

CALCULATE_HASHFILE_STARTED = "CALCULATE HASHFILE started"
CALCULATE_HASHFILE_COMPLETED = "CALCULATE HASHFILE completed"
CALCULATE_HASHFILE = "Calculate acquisition file hash"


GENERATE_PDF_REPORT = "Generate PDF Report"
GENERATE_PDF_REPORT_STARTED = "Generate PDF Report started"
GENERATE_PDF_REPORT_COMPLETED = "Generate PDF Report completed"

TAKE_FULL_PAGE_SCREENSHOT = "Take full page screenshot"
TAKE_FULL_PAGE_SCREENSHOT_STARTED = "Take full page screenshot started"
TAKE_FULL_PAGE_SCREENSHOT_COMPLETED = "Take full page screenshot completed"


SAVE_PAGE_STARTED = "Save page started"
SAVE_PAGE_COMPLETED = "Save page completed"
SAVE_PAGE = "Save all resource of current page"

SAVE_CASE_INFO_STARTED = "Save case information started"
SAVE_CASE_INFO_COMPLETED = "Save case information completed"
SAVE_CASE_INFO = "Save case information on json file"


ZIP_AND_REMOVE_FOLDER = "Zip and remove folder"
ZIP_AND_REMOVE_FOLDER_STARTED = "Zip and remove folder started"
ZIP_AND_REMOVE_FOLDER_COMPLETED = "Zip and remove folder completed"


TIMESTAMP_STARTED = "TIMESTAMP started"
TIMESTAMP_COMPLETED = "TIMESTAMP completed"
TIMESTAMP_APPLY = "Apply timestamp to {} from server {}"


PEC_AND_DOWNLOAD_EML_STARTED = "Send report by PEC and Download EML started"
PEC_AND_DOWNLOAD_EML_COMPLETED = "Send report by PEC and Download EML completed"
PEC_SENT = "Sent report by PEC to {} status {}"
PEC_HAS_NOT_BEEN_SENT_CANNOT_DOWNLOAD_EML = (
    "PEC has not been sent cannot download the EML"
)
EML_DOWNLOAD = "EML downloaded with status {}"


# MAIL SCRAPER
MAIL_SCRAPER_STARTED = "Mail Scraper started"
MAIL_SCRAPER_COMPLETED = "Mail Scraper completed"
MAIL_SCRAPER_LOGGED_IN = "Logged with mail: {}  {}"
MAIL_SCRAPER_SEARCH_EMAILS = "The email search is finished with status: {}"
MAIL_SCRAPER_FETCH_EMAILS = (
    "Fetching e-mails, estimated time: {} minutes, {} e-mail(s) found"
)
MAIL_SCRAPER_SEARCH_CRITERIA = "Start search emails whit criteria: {}"
MAIL_SCRAPER_DOWNLOAD_EMAILS = "Downloaded all selected emails"

# INSTAGRAM SCRAPER
INSTAGRAM_SCRAPER_STARTED = "Instagram Scraper started"
INSTAGRAM_SCRAPER_COMPLETED = "Instagram Scraper completed"
INSTAGRAM_SCRAPER_LOGGED_IN = "Logged with username: {} {}"
INSTAGRAM_SCRAPER_SCRAPE = "Scraping profile: {}"

# VIDEO SCRAPER
VIDEO_SCRAPER_STARTED = "Video Scraper started"
VIDEO_SCRAPER_COMPLETED = "Video Scraper completed"
VIDEO_SCRAPER_LOADED = "Loaded video from url {} with status {}"
VIDEO_SCRAPER_LOAD_FINISHED = "Loading video finished with status {}"
VIDEO_SCRAPER_DOWNLOADED = "Download video from url: {}"
VIDEO_SCRAPER_DOWNLOAD_FININISHED = "Download video has finished"

# ENTIRE WEBSITE SCRAPER
ENTIRE_WEBSITE_SCRAPER_STARTED = "Entire Website Scraper started"
ENTIRE_WEBSITE_SCRAPER_CHECK_IS_VALID_URL = (
    "Check vaild url: {} has finished whit status: {}"
)
ENTIRE_WEBSITE_SCRAPER_CHECK_IS_VALID_URL_FININISHED = (
    "Check vaild url has finished whit status: {}"
)
ENTIRE_WEBSITE_SCRAPER_URLS = "Get sitemap is finished with status: {}"
ENTIRE_WEBSITE_SCRAPER_DOWNLOADED = "Download entire website from url: {}"
ENTIRE_WEBSITE_DOWNLOAD_FININISHED = "Download entire website has finished"
ENTIRE_WEBSITE_ALL_PAGES_HAVE_BEEN_DOWNLOADED = "All pages have been downloaded"
DOWNLOADED = "Downloaded page {}"
