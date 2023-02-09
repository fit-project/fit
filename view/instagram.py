# !/usr/bin/env python3
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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from controller.instagram import Instagram as InstragramController

class Instagram(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        #aggiungere attributi per log, screencap ecc

    def init(self, case_info):
        self.setObjectName("mainWindow")
        self.resize(653, 392)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.input_username = QtWidgets.QLineEdit(self.centralwidget)
        self.input_username.setGeometry(QtCore.QRect(240, 30, 240, 20))
        self.input_username.setObjectName("input_username")

        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(240, 60, 240, 20))
        self.input_password.setObjectName("input_password")

        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setGeometry(QtCore.QRect(80, 30, 100, 20))
        self.label_username.setObjectName("label_username")
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(80, 60, 100, 20))
        self.label_password.setObjectName("label_password")
        self.scrapeButton = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton.setGeometry(QtCore.QRect(520, 270, 75, 25))
        self.scrapeButton.setObjectName("scrapeButton")

        self.scrapeButton.clicked.connect(self.button_clicked)
        self.scrapeButton.setEnabled(False)

        self.input_profile = QtWidgets.QLineEdit(self.centralwidget)
        self.input_profile.setGeometry(QtCore.QRect(240, 90, 240, 20))
        self.input_profile.setText("")
        self.input_profile.setObjectName("input_profile")

        # Verify if input fields are empty
        self.input_fields = [self.input_username, self.input_password, self.input_profile]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

        self.label_profile = QtWidgets.QLabel(self.centralwidget)
        self.label_profile.setGeometry(QtCore.QRect(80, 90, 141, 20))
        self.label_profile.setObjectName("label_profile")
        self.label_baseInfo = QtWidgets.QLabel(self.centralwidget)
        self.label_baseInfo.setGeometry(QtCore.QRect(80, 140, 111, 20))
        self.label_baseInfo.setObjectName("label_baseInfo")

        self.checkBox_post = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_post.setGeometry(QtCore.QRect(360, 170, 70, 17))
        self.checkBox_post.setObjectName("checkBox_post")

        self.checkBox_2_followee = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2_followee.setGeometry(QtCore.QRect(360, 190, 70, 17))
        self.checkBox_2_followee.setObjectName("checkBox_2_followee")

        self.checkBox_3_highlight = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3_highlight.setGeometry(QtCore.QRect(430, 190, 111, 17))
        self.checkBox_3_highlight.setObjectName("checkBox_3_highlight")

        self.checkBox_4_story = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4_story.setGeometry(QtCore.QRect(360, 230, 70, 17))
        self.checkBox_4_story.setObjectName("checkBox_4_story")

        self.checkBox_5_taggedPost = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5_taggedPost.setGeometry(QtCore.QRect(430, 210, 91, 17))
        self.checkBox_5_taggedPost.setObjectName("checkBox_5_taggedPost")

        self.checkBox_6_savedPost = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_6_savedPost.setGeometry(QtCore.QRect(430, 170, 91, 17))
        self.checkBox_6_savedPost.setObjectName("checkBox_6_savedPost")

        self.checkBox_7_follower = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_7_follower.setGeometry(QtCore.QRect(360, 210, 70, 17))
        self.checkBox_7_follower.setObjectName("checkBox_7_follower")

        self.label_optionalInfo = QtWidgets.QLabel(self.centralwidget)
        self.label_optionalInfo.setGeometry(QtCore.QRect(360, 140, 121, 20))
        self.label_optionalInfo.setObjectName("label_optionalInfo")
        self.label_completeName = QtWidgets.QLabel(self.centralwidget)
        self.label_completeName.setGeometry(QtCore.QRect(80, 170, 111, 20))
        self.label_completeName.setObjectName("label_completeName")
        self.label_biography = QtWidgets.QLabel(self.centralwidget)
        self.label_biography.setGeometry(QtCore.QRect(80, 190, 111, 20))
        self.label_biography.setObjectName("label_biography")
        self.label_numberOfPost = QtWidgets.QLabel(self.centralwidget)
        self.label_numberOfPost.setGeometry(QtCore.QRect(80, 210, 111, 20))
        self.label_numberOfPost.setObjectName("label_numberOfPost")
        self.label_profileImage = QtWidgets.QLabel(self.centralwidget)
        self.label_profileImage.setGeometry(QtCore.QRect(80, 230, 111, 20))
        self.label_profileImage.setObjectName("label_profileImage")
        self.label_accountType = QtWidgets.QLabel(self.centralwidget)
        self.label_accountType.setGeometry(QtCore.QRect(80, 250, 221, 20))
        self.label_accountType.setObjectName("label_accountType")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 653, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuConfiguration = QtWidgets.QMenu(self.menuBar)
        self.menuConfiguration.setObjectName("menuConfiguration")
        self.menuCase = QtWidgets.QMenu(self.menuBar)
        self.menuCase.setObjectName("menuCase")
        self.menuAcquisition = QtWidgets.QMenu(self.menuBar)
        self.menuAcquisition.setObjectName("menuAcquisition")
        self.setMenuBar(self.menuBar)
        self.menuBar.addAction(self.menuConfiguration.menuAction())
        self.menuBar.addAction(self.menuCase.menuAction())
        self.menuBar.addAction(self.menuAcquisition.menuAction())

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "Freezing Internet Tool"))
        self.label_username.setText(_translate("mainWindow", "Inserisci l\'username"))
        self.label_password.setText(_translate("mainWindow", "Inserisci la password"))
        self.scrapeButton.setText(_translate("mainWindow", "Scrape"))
        self.label_profile.setText(_translate("mainWindow", "Inserisci il nome dell\'profilo"))
        self.label_baseInfo.setText(_translate("mainWindow", "Informazioni di base:"))
        self.checkBox_post.setText(_translate("mainWindow", "Post"))
        self.checkBox_2_followee.setText(_translate("mainWindow", "Seguiti"))
        self.checkBox_3_highlight.setText(_translate("mainWindow", "Storie in evidenza"))
        self.checkBox_4_story.setText(_translate("mainWindow", "Storie"))
        self.checkBox_5_taggedPost.setText(_translate("mainWindow", "Post taggati"))
        self.checkBox_6_savedPost.setText(_translate("mainWindow", "Post salvati"))
        self.checkBox_7_follower.setText(_translate("mainWindow", "Seguaci"))
        self.label_optionalInfo.setText(_translate("mainWindow", "Informazioni aggiuntive:"))
        self.label_completeName.setText(_translate("mainWindow", "- Nome completo"))
        self.label_biography.setText(_translate("mainWindow", "- Biografia"))
        self.label_numberOfPost.setText(_translate("mainWindow", "- Numero di post"))
        self.label_profileImage.setText(_translate("mainWindow", "- Immagine profilo"))
        self.label_accountType.setText(_translate("mainWindow", "- Account verificato (si/no) e tipo di account"))
        self.menuConfiguration.setTitle(_translate("mainWindow", "Configuration"))
        self.menuCase.setTitle(_translate("mainWindow", "Case"))
        self.menuAcquisition.setTitle(_translate("mainWindow", "Acquisition"))

    def button_clicked(self):
        insta = InstragramController(self.input_username.text(), self.input_password.text(), self.input_profile.text(), "C:\\Users\\domen\\Desktop\\test")
        if(self.checkBox_post.isChecked()):
            try:
                insta.scrape_post()
            except Exception as e:
                print(e)
        if(self.checkBox_2_followee.isChecked()):
            insta.scrape_followees()
        if(self.checkBox_3_highlight.isChecked()):
            insta.scrape_highlights()
        if(self.checkBox_4_story.isChecked()):
            insta.scrape_stories()
        if(self.checkBox_5_taggedPost.isChecked()):
            insta.scrape_taggedPosts()
        if(self.checkBox_6_savedPost.isChecked()):
            insta.scrape_savedPosts()
        if(self.checkBox_7_follower.isChecked()):
            insta.scrape_followers()
        insta.scrape_info()
        insta.scrape_profilePicture()


    def onTextChanged(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.scrapeButton.setEnabled(all_field_filled)


