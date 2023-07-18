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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import yt_dlp
from youtube_comment_downloader import YoutubeCommentDownloader

from common.constants.view import video


class Video():
    def __init__(self):
        self.url = None
        self.ydl_opts = {'quiet': True, 'no-warnings': True}

        self.acquisition_dir = None
        self.title = None
        self.sanitized_name = None
        self.video_id = None
        self.id_digest = None
        self.thumbnail = None
        self.quality = None
        self.duration = None
        self.username = None
        self.password = None

    def set_url(self, url):
        self.url = url

    def set_quality(self, quality):
        self.quality = quality

    def set_auth(self, username, password):
        self.username = username
        self.password = password
        self.ydl_opts.update({
            'username': username,
            'password': password
        })

    # set output dir
    def set_dir(self, acquisition_dir):
        self.acquisition_dir = acquisition_dir
        self.ydl_opts.update({'outtmpl': acquisition_dir + '/' + self.id_digest + '.%(ext)s'})

    # download video and set id_digest for saving the file
    def download_video(self):
        if self.is_facebook_video():
            self.download_facebook_video()
        else:
            if self.quality == 'Lowest':
                self.ydl_opts['format'] = 'worstvideo'
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    ydl.extract_info(self.url, download=True)
                except:
                    pass  # can't download, skip for now

    # show thumbnail and video title
    def print_info(self):
        if self.is_facebook_video():
            self.id_digest = self.__calculate_md5(self.video_id)
            return None, video.NO_PREVIEW, None
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(self.url, download=False)
            self.video_id = video_info['id']
            self.id_digest = self.__calculate_md5(self.video_id)
            self.title = video_info['title']
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
    def get_video_id(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            self.id = video_info['id']

    # download video information
    def get_info(self):
        if self.is_facebook_video():
            return
        video_dir = os.path.join(self.acquisition_dir, self.video_id + '.json')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            with open(video_dir, 'w') as f:
                json.dump(ydl.sanitize_info(info), f)

    # check if video is from yt, but it's not a short
    def is_youtube_video(self):
        youtube_regex = r"(?:https?:\/\/)?(?:www\.)?youtu(?:\.be|be\.com)\/(?:watch\?v=|embed\/|v\/|\.+\?v=)?([\w\-]+)(?:\S+)?"
        shorts_regex = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([\w\-]+)(?:\S+)?"
        match = re.match(youtube_regex, self.url)
        if match:
            shorts_match = re.match(shorts_regex, self.url)
            return shorts_match is None
        return False

    # extract audio from video
    def get_audio(self):
        self.ydl_opts.update({
            'format': 'bestaudio',
            'keep-video': True,
        })
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(self.url)
        except:
            pass  # can't download audio, skip

    # download thumbnail
    def get_thumbnail(self):
        if self.is_facebook_video():
            return
        self.ydl_opts['format'] = 'best'
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

    def is_facebook_video(self):  # experimental
        facebook_url_pattern = r'(https?://)?(www\.)?facebook\.com/[a-zA-Z0-9./?=_-]+'
        is_facebook_url = re.match(facebook_url_pattern, self.url) is not None
        contains_videos = "videos" in self.url.lower()
        return is_facebook_url and contains_videos

    def __convert_seconds_to_hh_mm_ss(self, seconds):
        if seconds != 0:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return video.UNKNOWN

    def __calculate_md5(self, id):
        md5 = hashlib.md5()
        bytes = id.encode('utf-8')
        md5.update(bytes)
        md5_id = md5.hexdigest()
        return md5_id

    def download_facebook_video(self):
        options = webdriver.EdgeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}  # 1 to allow notifications, 2 to block
        )
        browser = webdriver.Edge(options=options)

        browser.get("https://www.facebook.com/login.php")
        wait = WebDriverWait(browser, 10)
        try:

            decline_cookies = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Decline optional cookies']")))
            decline_cookies.click()

            username = wait.until(EC.presence_of_element_located((By.ID, "email")))
            password = wait.until(EC.presence_of_element_located((By.ID, "pass")))
            submit = wait.until(EC.presence_of_element_located((By.ID, "loginbutton")))
            username.send_keys(self.username)
            password.send_keys(self.password)
            self.password = ''
            submit.click()

            browser.get(self.url)

            meatballs_menu = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Altro']")))
            meatballs_menu.click()

            download_item = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[download]')))
            download_item.click()

        except:
            browser.quit()
