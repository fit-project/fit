#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import youtube_dl


class Youtube():
    def __init__(self):
        super().__init__()
    def download_video(self, url,acquisition_directory):
        ydl_opts = {
            'outtmpl': acquisition_directory + '/%(title)s.%(ext)s',
            'quiet': True
        }
        dw = youtube_dl.YoutubeDL(ydl_opts)
        dw.download([url])