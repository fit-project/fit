#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import json
import yt_dlp

class Video():
    def __init__(self):
        self.url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'



#testing
url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    print(json.dumps(ydl.sanitize_info(info)))