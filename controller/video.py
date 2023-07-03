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
from bs4 import BeautifulSoup
from youtube_comment_downloader import YoutubeCommentDownloader

from common.constants.view import video


class Video():
    def __init__(self):
        self.url = None
        self.ydl_opts = {'quiet': True}
        self.acquisition_dir = None
        self.title = None
        self.sanitized_name = None
        self.video_id = None
        self.thumbnail = None
        self.quality = None
        self.duration = None

    def set_url(self, url):
        self.url = url

    def set_quality(self, quality):
        self.quality = quality

    # set output dir
    def set_dir(self, acquisition_dir):
        self.acquisition_dir = acquisition_dir
        self.ydl_opts.update({'outtmpl': acquisition_dir + '/%(title)s.%(ext)s'})

    # download video and set video_id for further operations
    def download_video(self):
        if self.quality == 'Lowest':
            self.ydl_opts['format'] = 'worstvideo'
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(self.url, download=True)
                self.video_id = info['id']
            except:
                pass #can't download, todo
                # self.__is_facebook_video()

    def __is_facebook_video(self):
        pattern = r"^(?:http[s]?://)?(?:www[.])?(?:facebook[.]com/|fb[.]me/|fb[.]com/)(?:.*)$"
        match = re.match(pattern, self.url)
        if match is not None:
            modified_url = self.url.replace("www.", "mbasic.")
            response = requests.get(modified_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            video_element = soup.find('video')

            if video_element and 'src' in video_element.attrs:
                video_url = video_element['src']
                print(video_url)

    # show thumbnail and video title
    def print_info(self):
        self.ydl_opts.update({
            'writethumbnail': True
        })
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(self.url, download=False)
            try:
                self.thumbnail = video_info['thumbnail']
            except:
                self.thumbnail = video.NO_PREVIEW
            try:
                self.duration = video_info['duration']
            except:
                self.duration = 0

            return self.title, self.thumbnail, self.__convert_seconds_to_hh_mm_ss(int(self.duration))

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
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(self.url)
        except:
            pass  # can't download audio, skip

    # download thumbnail
    def get_thumbnail(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.thumbnail])

    # download subtitles (if any)
    def get_subtitles(self):
        self.ydl_opts.update({
            'writesubtitles': True
        })
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(self.url)
        except:
            pass  # no subs, skip

    def get_comments(self):
        if 'youtube.com/watch' in self.url or 'youtu.be' in self.url:
            downloader = YoutubeCommentDownloader()
            file_path = os.path.join(self.acquisition_dir, 'video_comments.json')
            comments = list(downloader.get_comments_from_url(self.url, sort_by=0))  # 0 = popular
            with open(file_path, 'w') as f:
                json.dump(comments, f)
        # else: not a youtube video, skip

    def create_zip(self, path):
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                shutil.make_archive(folder_path, 'zip', folder_path)
                shutil.rmtree(folder_path)

    def __convert_seconds_to_hh_mm_ss(self, seconds):
        if seconds != 0:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return video.UNKNOWN