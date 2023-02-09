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

from instaloader import Instaloader, Profile
import os

class Instagram:
    def __init__(self, username, password, profileName, path):
        self.username = username
        # TODO: implement secure password handling
        self.password = password
        self.profileName = profileName
        self.loader = Instaloader()
        self.profile = Profile.from_username(self.loader.context, profileName)
        self.path = path
        os.chdir(self.path)
        return

    def login(self):
        self.loader.login(self.username, self.password)
        return

    def scrape_post(self):
        os.chdir(self.path)
        if (self.profile.is_private == True):
            self.login()
        posts = self.profile.get_posts()
        os.makedirs(self.profileName + "_posts")
        print("qui")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_posts")
        print("prima dell'if")
        for post in posts:
            self.loader.download_post(post, self.profileName)
            print("for")

        return

    def scrape_stories(self):
        os.chdir(self.path)
        self.login()
        id = []
        id.append(self.profile.userid)
        os.makedirs(self.profileName + "_stories")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_stories")
        self.loader.download_stories(id, None)
        return

    def scrape_followers(self):
        os.chdir(self.path)
        self.login()
        nFollowers = self.profile.followers
        followers = self.profile.get_followers()
        os.makedirs(self.profileName + "_profileFollowers")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_profileFollowers")
        file = open(self.profile.username + "_followers.txt", "w")
        file.write("Numero di followers: " + str(nFollowers) + "\n")
        file.write("\n")
        file.write("Followers:\n")
        for follower in followers:
            file.write(follower.username + "\n")
        file.close()
        return

    def scrape_followees(self):
        os.chdir(self.path)
        self.login()
        nFollowees = self.profile.followees
        followees = self.profile.get_followees()
        os.makedirs(self.profileName + "_profileFollowees")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_profileFollowees")
        file = open(self.profile.username + "_followees.txt", "w")
        file.write("Numero di followees: " + str(nFollowees) + "\n")
        file.write("\n")
        file.write("Followees:\n")
        for followee in followees:
            file.write(followee.username + "\n")
        file.close()
        return

    def scrape_savedPosts(self):
        os.chdir(self.path)
        self.login()
        savedPosts = self.profile.get_saved_posts()
        os.makedirs(self.profileName + "_savedPosts")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_savedPosts")
        for savedPost in savedPosts:
            self.loader.download_post(savedPost, self.profile)
        return

    def scrape_profilePicture(self):
        os.chdir(self.path)
        os.makedirs(self.profileName + "_profilePic")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_profilePic")
        self.loader.download_profilepic(self.profile)
        return

    def scrape_taggedPosts(self):
        os.chdir(self.path)
        if (self.profile.is_private == True):
            self.login()
        taggedPosts = self.profile.get_tagged_posts()
        os.makedirs(self.profileName + "_taggedPosts")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_taggedPosts")
        for taggedPost in taggedPosts:
            self.loader.download_post(taggedPost, self.profile)
        return

    def scrape_info(self):
        os.chdir(self.path)
        verified = self.profile.is_verified
        fullName = self.profile.full_name
        businessCategory = self.profile.business_category_name
        biography = self.profile.biography
        nMedia = self.profile.mediacount
        os.makedirs(self.profileName + "_profileInfo")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_profileInfo")
        file = open(self.profile.username + "_profileInfo.txt", "w")
        if (verified == True):
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
        file.close()
        return

    def scrape_highlights(self):
        os.chdir(self.path)
        self.login()
        os.makedirs(self.profileName + "_highlights")
        os.chdir(os.getcwd() + "\\" + self.profileName + "_highlights")
        self.loader.download_highlights(self.profile.userid)
        return
