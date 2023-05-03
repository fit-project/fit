#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######
from pathlib import Path
from instaloader import Instaloader, Profile
import os

class Instagram:
    def __init__(self, username, password, profileName, path):
        self.username = username
        self.password = password
        self.profileName = profileName
        self.loader = Instaloader()
        self.profile = None
        self.path = path

    def login(self):
        self.loader.login(self.username, self.password)
        self.profile = Profile.from_username(self.loader.context, self.profileName)

    def scrape_post(self):
        if self.profile.is_private:
            self.login()
        posts = self.profile.get_posts()
        for post in posts:
            self.loader.download_post(post, Path(os.path.join(self.path, self.profileName)))

    def scrape_stories(self):
        self.login()
        id = []
        id.append(self.profile.userid)
        self.loader.download_stories(id, Path(os.path.join(self.path, self.profileName)))

    def scrape_followers(self):
        self.login()
        nFollowers = self.profile.followers
        followers = self.profile.get_followers()
        file = open(os.path.join(self.path,"followers.txt"), "w")
        file.write("Numero di followers: " + str(nFollowers) + "\n")
        file.write("\n")
        file.write("Followers:\n")
        for follower in followers:
            file.write(follower.username + "\n")
        file.close()

    def scrape_followees(self):
        self.login()
        nFollowees = self.profile.followees
        followees = self.profile.get_followees()

        file = open(os.path.join(self.path,"followees.txt"), "w")
        file.write("Numero di followees: " + str(nFollowees) + "\n")
        file.write("\n")
        file.write("Followees:\n")
        for followee in followees:
            file.write(followee.username + "\n")
        file.close()

    def scrape_savedPosts(self):
        self.login()
        savedPosts = self.profile.get_saved_posts()
        for savedPost in savedPosts:
            self.loader.download_post(savedPost, Path(os.path.join(self.path, self.profileName)))
        return

    def scrape_profilePicture(self):

        self.loader.download_profilepic(self.profile)
        return

    def scrape_taggedPosts(self):
        if self.profile.is_private:
            self.login()
        taggedPosts = self.profile.get_tagged_posts()

        for taggedPost in taggedPosts:
            self.loader.download_post(taggedPost, Path(os.path.join(self.path, self.profileName)))
        return

    def scrape_info(self):
        verified = self.profile.is_verified
        fullName = self.profile.full_name
        businessCategory = self.profile.business_category_name
        biography = self.profile.biography
        nMedia = self.profile.mediacount
        file = open(os.path.join(self.path,"profileInfo.txt"), "w")
        if verified:
            file.write("Tipo di profilo: verificato" + "\n")
        else:
            file.write("Tipo di profilo: non verificato" + "\n")
        file.write("Nome completo: " + fullName + "\n")
        if (businessCategory is None):
            file.write("Tipo di account: " + "personale" + "\n")
        else:
            file.write("Tipo di account: " + str(businessCategory) + "\n")
        file.write("Biografia account: " + biography + "\n")
        file.write("Numero di post: " + str(nMedia))
        file.flush()
        file.close()
        return

    def scrape_highlights(self):
        self.login()
        os.makedirs(self.profileName + "_highlights")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_highlights")
        self.loader.download_highlights(self.profile.userid)
        return
