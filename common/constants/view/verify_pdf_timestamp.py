#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

VERIFICATION_COMPLETED = "Verification completed"
VERIFICATION_SUCCESS = "Timestamp has been verified successfully."
VERIFICATION_FAIL = "Timestamp verification failed."
VALID_TIMESTAMP_REPORT = (
    "PDF has a valid timestamp, report has been generated. Do you want to open it?"
)
INVALID_TIMESTAMP_REPORT = "PDF may have been tampered with, report has been generated."
VALID_TIMESTAMP = "PDF has a valid timestamp."
INVALID_TIMESTAMP = "PDF may have been tampered with."
TIMESTAMP_SETTINGS = "Timestamp settings"
PDF_LABEL = "Report (.pdf)"
TSR_LABEL = "Timestamp (.tsr)"
CRT_LABEL = "TSA Certificate (.crt)"
OPEN_PDF_FILE = "Open PDF"
OPEN_TSR_FILE = "Open timestamp"
OPEN_CRT_FILE = "Open certificate"
PDF_FILE = "PDF Files (*.pdf)"
TSR_FILE = "TSR Files (*.tsr)"
CRT_FILE = "CERT Files (*.crt)"

REPORT_LABEL_RESULT = "ESITO"
REPORT_LABEL_FILENAME = "NOME DEL FILE"
REPORT_LABEL_SIZE = "DIMENSIONE"
REPORT_LABEL_HASH_ALGORITHM = "ALGORITMO DI HASHING"
REPORT_LABEL_DIGEST = "DIGEST"
REPORT_LABEL_TIMESTAMP = "TIMESTAMP"
REPORT_LABEL_SERVER = "SERVER"
REPORT_LABEL_SHA256 = "sha-256"

CHECK_TIMESTAMP_SERVER = "Check timestamper server on URL: {}"
CHECK_TIMESTAMP_SERVER_FAIL = "Without the correct timestamp server, you cannot continue. Please check your configuration and try again!"
VERIFY_TIMESTAMP = "Verify timestamp"
VERIFY_TIMESTAMP_FAIL = (
    "Without the timestamp verification result, you cannot continue. Please try again!"
)
GENERATE_FILE_TIMESTAMP_INFO = "Generate file timestamp_info.txt"
GENERATE_FILE_TIMESTAMP_INFO_FAIL = (
    "Without file timestamp_info.txt, you cannot continue. Please try again!"
)
GENARATE_REPORT = "Generate report"
