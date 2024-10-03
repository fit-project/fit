#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
TITLE = "Case Info"
NAME = "Client/Case # *"
LAWYER = "Lawyer"
OPERATOR = "Operator"
PROCEEDING_TYPE = "Proceeding Type"
COURTHOUSE = "Courthouse"
PROCEEDING_NUMBER = "Proceeding Number"
NOTES = "Note"
DIALOG_TITLE = " Case {} ID: {}"
LOGO = "Logo"
LOGO_INFO = "Minimum width: {}px, Format: {}, Background: {}"
SELECT_EMPTY_LOGO = "Browse..."
SELECT_FULL_LOGO = "Change..."
SELECT_PROCEEDING_TYPE = "Select proceeding type..."
SELECT_CASE_NAME = "Select case or insert new one..."

CHECK_SELECTED_LOGO = "Check logo file"
ERR_SELECTED_LOGO_FORMAT = "The allowed formats are {}. Selected image format is {}"
ERR_SELECTED_LOGO_MINIMUM_WIDTH = (
    "The allowed minimum width is {}px. Selected image has width {}px"
)
TEMPORARY_CASE_NAME = "Temporary"
ERR_SELECTED_LOGO_BG_COLOR = "The allowed background colors are {}."
WAR_NOT_CASE_INFO_JSON_FILE_FOUND = 'The <i><strong>case_info.json</strong></i> file was not found!.<br><br>Do you want to insert the information needed to generate the report (<strong>it will not be saved in the DB</strong>)?<br><br><strong style="color:red">If you don\'t insert any information, in the report the case will be identified as UNKNOWN!</strong>'
