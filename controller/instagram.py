#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import shutil

from pathlib import Path
from instaloader import Instaloader, Profile, instaloader
import os

from common.constants.controller import instagram


# Override default handle_429 behavior to manage error 429 by UI.
# https://instaloader.github.io/module/instaloadercontext.html#instaloader.RateController
# https://instaloader.github.io/troubleshooting.html#too-many-requests
#“Too many queries in the last time” is not an error. 
# It is a notice that the rate limit has almost been reached, according to Instaloader’s
# own rate accounting mechanism.Instaloader allows to adjust the rate controlling behavior by overriding instaloader.RateController
class InstagramRateController(instaloader.RateController):
  def handle_429(self, query_type: str) -> None:
        raise Exception(instagram.HANDLE_429)

class Instagram():
    def __init__(self):
        self.loader = instaloader.Instaloader(rate_controller=lambda ctx: InstagramRateController(ctx))
        self.profile = None
        self.username = None
        self.username = None
        self.profile_name = None
        self.is_logged_in = False

    def set_login_information(self, username, password, profile_name):
        self.username = username
        self.password = password
        self.profile_name = profile_name

    def login(self):
        self.loader.login(self.username, self.password)
        try:
            self.profile = Profile.from_username(self.loader.context, self.profile_name)
            self.is_logged_in = True

        except Exception as e:
            raise Exception(e)


    def set_dir(self, path):
        self.path = path
        self.loader.dirname_pattern = self.path

    def scrape_post(self):
        posts = self.profile.get_posts()
        for post in posts:
            self.loader.download_post(post, self.profile_name)

    def scrape_stories(self):
        id = []
        id.append(self.profile.userid)
        self.loader.download_stories(id, Path(self.__make_scraped_type_directory("stories")))

    def scrape_followers(self):
        n_followers = self.profile.followers
        followers = self.profile.get_followers()
        file = open(os.path.join(self.__make_scraped_type_directory("followers"), "followers.txt"), "w", encoding="utf-8")
        file.write(instagram.N_FOLLOWERS + str(n_followers) + "\n")
        file.write("\n")
        file.write(instagram.FOLLOWERS)
        for follower in followers:
            file.write(follower.username + "\n")
        file.close()

    def scrape_followees(self):
        n_followees = self.profile.followees
        followees = self.profile.get_followees()

        file = open(os.path.join(self.__make_scraped_type_directory("followees"), "followees.txt"), "w", encoding="utf-8")
        file.write(instagram.N_FOLLOWEES + str(n_followees) + "\n")
        file.write("\n")
        file.write(instagram.FOLLOWEES)
        for followee in followees:
            file.write(followee.username + "\n")
        file.close()

    def scrape_saved_posts(self):
        tmp_context_username = None

        if self.profile.username != self.profile._context.username:

            tmp_context_username = self.profile._context.username
            self.profile._context.username = self.profile.username
  
        saved_posts = self.profile.get_saved_posts()

        if tmp_context_username is not None:
            self.profile._context.username = tmp_context_username

        for saved_post in saved_posts:
            self.loader.download_post(saved_post, Path(self.__make_scraped_type_directory("saved_posts")))
        

    def scrape_profile_picture(self):
        self.loader.download_profilepic(self.profile)
        

    def scrape_tagged_posts(self):
        tagged_posts = self.profile.get_tagged_posts()

        for tagged_post in tagged_posts:
            self.loader.download_post(tagged_post, Path(self.__make_scraped_type_directory("tagged_posts")))
        

    def scrape_info(self):
        verified = self.profile.is_verified
        full_name = self.profile.full_name
        business_category = self.profile.business_category_name
        biography = self.profile.biography
        n_media = self.profile.mediacount
        file = open(os.path.join(self.path, "profile_info.txt"), "w", encoding="utf-8")
        if verified:
            file.write(instagram.VERIFIED + "\n")
        else:
            file.write(instagram.NO_VERIFIED + "\n")
        file.write(instagram.FULL_NAME + full_name + "\n")
        if not business_category:
            file.write(instagram.PERSONAL + "\n")
        else:
            file.write(instagram.TYPE + str(business_category) + "\n")
        file.write(instagram.BIO + biography + "\n")
        file.write(instagram.N_POSTS + str(n_media))
        file.flush()
        file.close()
        

    def scrape_highlights(self):
        self.loader.download_highlights(self.profile.userid)
    
    def __make_scraped_type_directory(self, directory_name):

        scraped_type_directory = os.path.join(self.path, self.profile_name, directory_name)
        if not os.path.exists(scraped_type_directory):
            os.makedirs(scraped_type_directory)

        return scraped_type_directory

    def create_zip(self, path):
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                zip_file = folder + '.zip'
                zip_file_path = os.path.join(path, zip_file)
                shutil.make_archive(zip_file_path, 'zip', folder_path)
                shutil.rmtree(folder_path)
        
