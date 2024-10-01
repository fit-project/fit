#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

SCREEN_RECODER = (
    "An error occurred during screen recoder acquisition! \nSee bellow for more detail."
)

PREVIEW_ERROR_NOT_VALID_WINDOW_TITLE = "Invalid window"
PREVIEW_ERROR_NOT_VALID_WINDOW_MSG = 'The window selected is no longer valid.<br><br><strong style="color:red"> It is necessary update the list of windows to setup another primary screen!</strong>'
PREVIEW_WINDOW_CAPTURE_ERROR_OCCURED_TITLE = "QWindowCapture: Error occurred"
PREVIEW_SCREEN_CAPTURE_ERROR_OCCURED_TITLE = "QScreenCapture: Error occurred"

SCREENS_CHANGED_TILE = "Screen changed"
SCREENS_CHANGED_SCREEN_ADDED_MSG = (
    "A new screen has been added. Do you want setup it as primary screen?"
)
SCREENS_CHANGED_SCREEN_REMOVED_MSG = 'A screen has been removed.<br><br><strong style="color:red"> It is necessary to setup the primary screen!</strong>'
SCREENS_PRIMARY_SCREEN_CHANGED_MSG = 'Primary screen changed.<br><br><strong style="color:red"> It is necessary to setup the primary screen!</strong>'

MULTIPLE_SCREEN_TITLE = "Multiple Screen"
MULTIPLE_SCREEN_MSG = "There are {} screens connected to your PC! Do you want setup a specific one as primary screen?"

SETTING_SCREEN_BEFORE_ACQUISITION_START_TITLE = "Setting Screen"
SETTING_SCREEN_BEFORE_ACQUISITION_START_MSG = "Before starting the acquisition, <strong>it is necessary</strong> to check the settings of the screen to be recorded"


FFMPEG_INSTALLED = "FFmpeg is installed"
FFMPEG_NOT_INSTALLED = "FFmpeg is not installed"

VB_CABLE_INSTALLED = "VB-CABLE is installed"
VB_CABLE_NOT_INSTALLED = "VB-CABLE is not installed"

VB_CABLE_FIRST_OUPUT_AUDIO_DEVICE = "VB-CABLE is first output audio device"
VB_CABLE_NOT_FIRST_OUPUT_AUDIO_DEVICE = "VB-CABLE is not first output audio device"

AUDIO_RECORDING_MANAGEMENT_GUIDE_URL = "https://github.com/fit-project/fit/wiki/Screen-recording-audio-and-video-management"
AUDIO_RECORDING_MANAGEMENT_GUIDE = (
    "<strong><i><u>For more info read the guide</u></i></strong>"
)
