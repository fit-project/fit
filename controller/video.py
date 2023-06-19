#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import hashlib
import json
import os
import re
import shutil

import yt_dlp


class Video():
    def __init__(self):
        self.url = None
        self.ydl_opts = {'quiet': True}
        self.acquisition_dir = None
        self.sanitized_name = None

    def set_url(self, url):
        self.url = url

    # set output dir
    def set_dir(self, acquisition_dir):
        self.acquisition_dir = acquisition_dir
        self.ydl_opts.update({'outtmpl': acquisition_dir + '/%(title)s.%(ext)s'})

    # download video in mp4 (default)
    def download_video(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.extract_info(self.url, download=True)

    # extract video title and sanitize it
    def create_video_title_sanitized(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            title = video_info['title']
            sanitized_name = re.sub(r'[<>:"/\\|?*]', '', title)
            self.sanitized_name = sanitized_name
            return self.sanitized_name

    # download video information
    def scrape_info(self):
        video_dir = os.path.join(self.acquisition_dir, self.sanitized_name + '.json')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            with open(video_dir, 'w') as f:
                json.dump(ydl.sanitize_info(info), f)

    # extract audio from video
    def extract_audio(self):
        self.ydl_opts.update({
            'format': 'bestaudio',
            'k': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio'
            }]
        })
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(self.url)

        # extract thumbnail from video
    def extract_thumbnail(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(self.url, download=False)
            if 'thumbnail' in video_info:
                thumbnail = video_info['thumbnail']
                ydl.download([thumbnail])

    def create_zip(self, path):
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                shutil.make_archive(folder_path, 'zip', folder_path)
                shutil.rmtree(folder_path)
