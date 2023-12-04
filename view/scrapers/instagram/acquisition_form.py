# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtGui, QtWidgets
from common.constants.view import instagram, general


class InstagramAcquisitionForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InstagramAcquisitionForm, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        # ACQUISITION GROUP BOX
        self.acquisition_group_box = QtWidgets.QGroupBox(self.parent())
        self.acquisition_group_box.setFont(font)
        self.acquisition_group_box.setEnabled(False)
        self.acquisition_group_box.setGeometry(QtCore.QRect(50, 200, 430, 180))
        self.acquisition_group_box.setObjectName("acquisition_group_box")

        # BASIC INFORMATION
        self.label_base_info = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_base_info.setGeometry(QtCore.QRect(20, 30, 111, 20))
        self.label_base_info.setFont(font)
        self.label_base_info.setObjectName("label_base_info")

        self.label_complete_name = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_complete_name.setGeometry(QtCore.QRect(20, 50, 111, 20))
        self.label_complete_name.setFont(font)
        self.label_complete_name.setObjectName("label_complete_name")

        self.label_biography = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_biography.setGeometry(QtCore.QRect(20, 70, 111, 20))
        self.label_biography.setFont(font)
        self.label_biography.setObjectName("label_biography")

        self.label_number_of_post = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_number_of_post.setGeometry(QtCore.QRect(20, 90, 111, 20))
        self.label_number_of_post.setFont(font)
        self.label_number_of_post.setObjectName("label_number_of_post")

        self.label_profile_image = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_profile_image.setGeometry(QtCore.QRect(20, 110, 111, 20))
        self.label_profile_image.setFont(font)
        self.label_profile_image.setObjectName("label_profile_image")

        self.label_account_type = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_account_type.setGeometry(QtCore.QRect(20, 130, 221, 20))
        self.label_account_type.setFont(font)
        self.label_account_type.setObjectName("label_account_type")

        # ADDITIONAL_INFORMATION
        self.label_aditional_information = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_aditional_information.setGeometry(QtCore.QRect(230, 30, 150, 20))
        self.label_aditional_information.setFont(font)
        self.label_aditional_information.setObjectName("label_aditional_information")

        self.checkbox_post = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_post.setGeometry(QtCore.QRect(230, 50, 70, 17))
        self.checkbox_post.setFont(font)
        self.checkbox_post.setObjectName("scrape_post")

        self.checkbox_followee = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_followee.setGeometry(QtCore.QRect(230, 70, 90, 17))
        self.checkbox_followee.setFont(font)
        self.checkbox_followee.setObjectName("scrape_followees")

        self.checkbox_story = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_story.setGeometry(QtCore.QRect(230, 90, 70, 17))
        self.checkbox_story.setFont(font)
        self.checkbox_story.setObjectName("scrape_stories")

        self.checkbox_follower = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_follower.setGeometry(QtCore.QRect(230, 110, 90, 17))
        self.checkbox_follower.setFont(font)
        self.checkbox_follower.setObjectName("scrape_followers")

        self.checkbox_highlight = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_highlight.setGeometry(QtCore.QRect(230, 130, 111, 17))
        self.checkbox_highlight.setFont(font)
        self.checkbox_highlight.setObjectName("scrape_highlights")

        self.checkbox_tagged_post = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_tagged_post.setGeometry(QtCore.QRect(320, 50, 100, 17))
        self.checkbox_tagged_post.setFont(font)
        self.checkbox_tagged_post.setObjectName("scrape_tagged_posts")

        self.checkbox_saved_post = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_saved_post.setGeometry(QtCore.QRect(320, 70, 100, 17))
        self.checkbox_saved_post.setFont(font)
        self.checkbox_saved_post.setObjectName("scrape_saved_posts")

        self.scrape_button = QtWidgets.QPushButton(self.acquisition_group_box)
        self.scrape_button.setGeometry(QtCore.QRect(350, 145, 70, 25))
        self.scrape_button.setObjectName("scrapeButton")
        self.scrape_button.setFont(font)
        self.scrape_button.setEnabled(False)

        self.retranslateUi()

    def retranslateUi(self):
        self.acquisition_group_box.setTitle(instagram.ACQUISITON_SETTINGS)
        self.label_base_info.setText(
            "<strong>" + instagram.BASIC_INFORMATION + "</strong>"
        )
        self.label_complete_name.setText(instagram.FULL_NAME)
        self.label_biography.setText(instagram.BIO)
        self.label_number_of_post.setText(instagram.POST_NUMBER)
        self.label_profile_image.setText(instagram.PROFILE_PIC)
        self.label_account_type.setText(instagram.ACCOUNT_TYPE)
        self.label_aditional_information.setText(
            "<strong>" + instagram.ADDITIONAL_INFORMATION + "</strong>"
        )
        self.checkbox_post.setText(instagram.POST)
        self.checkbox_followee.setText(instagram.FOLLOWING)
        self.checkbox_highlight.setText(instagram.HIGHLIGHTS)
        self.checkbox_story.setText(instagram.STORIES)
        self.checkbox_tagged_post.setText(instagram.TAGGED)
        self.checkbox_saved_post.setText(instagram.SAVED)
        self.checkbox_follower.setText(instagram.FOLLOWERS)
        self.scrape_button.setText(general.BUTTON_SCRAPE)

    def enable_acquisition(self, enable):
        self.acquisition_group_box.setEnabled(enable)
        self.scrape_button.setEnabled(enable)
