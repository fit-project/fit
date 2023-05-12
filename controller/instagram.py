#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
from pathlib import Path
from instaloader import Instaloader, Profile
import os
from common.constants.controller import instagram


class Instagram:
    def __init__(self, username, password, profile_name):
        self.username = username
        self.password = password
        self.profile_name = profile_name
        self.loader = Instaloader()
        self.profile = None
        self.is_logged_in = False

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
        if self.profile.is_private:
            self.login()
        posts = self.profile.get_posts()
        for post in posts:
            self.loader.download_post(post, Path(os.path.join(self.path, self.profile_name)))

    def scrape_stories(self):
        self.login()
        id = []
        id.append(self.profile.userid)
        self.loader.download_stories(id, Path(os.path.join(self.path, self.profile_name)))

    def scrape_followers(self):
        self.login()
        n_followers = self.profile.followers
        followers = self.profile.get_followers()
        file = open(os.path.join(self.path, "followers.txt"), "w", encoding="utf-8")
        file.write(instagram.N_FOLLOWERS + str(n_followers) + "\n")
        file.write("\n")
        file.write(instagram.FOLLOWERS)
        for follower in followers:
            file.write(follower.username + "\n")
        file.close()

    def scrape_followees(self):
        self.login()
        n_followees = self.profile.followees
        followees = self.profile.get_followees()

        file = open(os.path.join(self.path, "followees.txt"), "w", encoding="utf-8")
        file.write(instagram.N_FOLLOWEES + str(n_followees) + "\n")
        file.write("\n")
        file.write(instagram.FOLLOWEES)
        for followee in followees:
            file.write(followee.username + "\n")
        file.close()

    def scrape_saved_posts(self):
        self.login()
        saved_posts = self.profile.get_saved_posts()
        for saved_post in saved_posts:
            self.loader.download_post(saved_post, Path(os.path.join(self.path, self.profile_name)))
        return

    def scrape_profile_picture(self):
        self.loader.download_profilepic(self.profile)
        return

    def scrape_tagged_posts(self):
        if self.profile.is_private:
            self.login()
        tagged_posts = self.profile.get_tagged_posts()

        for tagged_post in tagged_posts:
            self.loader.download_post(tagged_post, Path(os.path.join(self.path, self.profile_name)))
        return

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
        return

    def scrape_highlights(self):
        self.login()
        self.loader.download_highlights(self.profile.userid)
        return
