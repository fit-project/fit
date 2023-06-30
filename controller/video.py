#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import json
import os
import re
import shutil

import requests
import yt_dlp
from youtube_comment_downloader import YoutubeCommentDownloader


class Video():
    def __init__(self):
        self.url = None
        self.ydl_opts = {'quiet': True, "cookies-from-browser": "edge"}
        self.acquisition_dir = None
        self.title = None
        self.sanitized_name = None
        self.video_id = None
        self.thumbnail = None

    def set_url(self, url):
        self.url = url

    # set output dir
    def set_dir(self, acquisition_dir):
        self.acquisition_dir = acquisition_dir
        self.ydl_opts.update({'outtmpl': acquisition_dir + '/%(title)s.%(ext)s'})

    # download video and set video_id for further operations
    def download_video(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            self.video_id = info['id']

    def print_info(self):
        self.ydl_opts.update({
            'writethumbnail': True
        })
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(self.url, download=False)
            self.thumbnail = video_info['thumbnail']
            return self.title, self.thumbnail


    # extract video title and sanitize it
    def get_video_title_sanitized(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            self.title = video_info['title']
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '', self.title)
        self.sanitized_name = sanitized_name
        return self.sanitized_name

    # download video information
    def get_info(self):
        video_dir = os.path.join(self.acquisition_dir, self.sanitized_name + '.json')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            with open(video_dir, 'w') as f:
                json.dump(ydl.sanitize_info(info), f)

    # extract audio from video
    def get_audio(self):
        self.ydl_opts.update({
            'format': 'bestaudio',
            'keep-video': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio'
            }]
        })
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(self.url)


    # extract thumbnail from video
    def get_thumbnail(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.thumbnail])

    # download subtitles (if any)
    def get_subtitles(self):
        self.ydl_opts.update({
            'writesubtitles': True
        })
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(self.url)

    def get_comments(self):
        if 'youtube.com/watch' in self.url or 'youtu.be' in self.url:
            downloader = YoutubeCommentDownloader()
            file_path = os.path.join(self.acquisition_dir,'video_comments.json')
            comments = list(downloader.get_comments_from_url(self.url,
                                                        sort_by=0)) # 0 =popular
            with open(file_path, 'w') as f:
                json.dump(comments, f)
        #else: not a youtube video

    def create_zip(self, path):
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                shutil.make_archive(folder_path, 'zip', folder_path)
                shutil.rmtree(folder_path)
