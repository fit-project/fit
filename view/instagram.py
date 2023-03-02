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
import os
import shutil
import zipfile

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from instaloader import InvalidArgumentException, BadCredentialsException, ConnectionException, \
    ProfileNotExistsException
from controller.instagram import Instagram as InstragramController
from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView
from common.error import ErrorMessage
from common.settings import DEBUG
from common.config import LogConfigMail
import common.utility as utility
from view.acquisitionstatus import AcquisitionStatus as AcquisitionStatusView
from view.verify_pdf_timestamp import VerifyPDFTimestamp as VerifyPDFTimestampView
from view.timestamp import Timestamp as TimestampView
from controller.report import Report as ReportController
import logging
import logging.config

logger_acquisition = logging.getLogger(__name__)
logger_hashreport = logging.getLogger('hashreport')

class Instagram(QtWidgets.QMainWindow):
    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

    def _acquisition_status(self):
        self.acquisition_status.show()

    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        self.error_msg = ErrorMessage()
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.is_enabled_timestamp = False
        self.acquisition_status = AcquisitionStatusView(self)
        self.acquisition_status.setupUi()
        self.log_confing = LogConfigMail()
        #aggiungere attributi per log, screencap ecc

    def init(self, case_info):
        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.setObjectName("mainWindow")
        self.resize(653, 392)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menuConfiguration = QtWidgets.QAction("Configuration", self)
        self.menuConfiguration.setObjectName("menuConfiguration")
        self.menuConfiguration.triggered.connect(self.configuration)
        self.menuBar().addAction(self.menuConfiguration)

        # CASE BUTTON
        self.case_action = QtWidgets.QAction("Case", self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.case)
        self.menuBar().addAction(self.case_action)

        # ACQUISITION BUTTON
        self.acquisition_menu = self.menuBar().addMenu("&Acquisition")
        self.acquisition_status_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'info.png')),
                                                           "Status",
                                                           self)
        self.acquisition_status_action.triggered.connect(self._acquisition_status)
        self.acquisition_status_action.setObjectName("StatusAcquisitionAction")
        self.acquisition_menu.addAction(self.acquisition_status_action)

        # VERIFY PDF ACTION
        verify_pdf_action = QtWidgets.QAction("Verify timestamp", self)
        verify_pdf_action.setStatusTip("Verify the timestamp of a report")
        verify_pdf_view = VerifyPDFTimestampView()
        verify_pdf_view.init(self.case_info)
        verify_pdf_action.triggered.connect(verify_pdf_view.show)
        self.menuBar().addAction(verify_pdf_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        # Get timestamp parameters
        self.configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")

        self.input_username = QtWidgets.QLineEdit(self.centralwidget)
        self.input_username.setGeometry(QtCore.QRect(240, 30, 240, 20))
        self.input_username.setObjectName("input_username")

        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(240, 60, 240, 20))
        self.input_password.setObjectName("input_password")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)

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
        self.progressBar.setValue(0)
        self.progressBar.setObjectName("progressBar")

        self.labelStatus = QtWidgets.QLabel(self.centralwidget)
        self.labelStatus.setGeometry(QtCore.QRect(80, 280, 120, 24))
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.resize(300, 80)
        self.labelStatus.show()

        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

        # Enable/Disable other modules logger
        if not DEBUG:
            loggers = [logging.getLogger()]  # get the root logger
            loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict if
                                 name not in [__name__, 'hashreport']]

            self.log_confing.disable_loggers(loggers)

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

    def button_clicked(self):
        originalPath = os.getcwd()
        #Disable start_acquisition_action and clear current threads and acquisition information on dialog
        action = self.findChild(QtWidgets.QAction, 'StartAcquisitionAction')
        if action is not None:
            action.setEnabled(False)

        self.acquisition_status.clear()
        self.acquisition_status.set_title('Acquisition is started')

        self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
            'instagram',
            self.configuration_general.configuration['cases_folder_path'],
            self.case_info['name'],
            self.input_profile.text()
        )

        self.acquisition_status.set_title('Acquisition in progress')
        self.acquisition_status.add_task('Case Folder')
        self.acquisition_status.set_status('Case Folder', self.acquisition_directory, 'done')
        #self.status.showMessage(self.acquisition_directory)

        self.log_confing.change_filehandlers_path(self.acquisition_directory)
        logging.config.dictConfig(self.log_confing.config)

        logger_acquisition.info('Acquisition started')
        logger_acquisition.info(f'NTP start acquisition time: {utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])}')

        self.acquisition_status.add_task('Logger')
        self.acquisition_status.set_status('Logger', 'Started', 'done')
        #self.status.showMessage('Logging handler and login information have been started')

        self.acquisition_status.set_title('Acquisition started success')

        error = False
        self.labelStatus.setText("")
        self.progressBar.setValue(0)
        insta = InstragramController(self.input_username.text(), self.input_password.text(), self.input_profile.text(), self.acquisition_directory)

        try:
            logger_acquisition.info('Login into Instagram account')
            insta.login()
        except InvalidArgumentException:
            error = True
            self.labelStatus.setText("Errore:\nL'username fornito non esiste...")
            logger_acquisition.info('Errore: l''username fornito non esiste')
            logger_acquisition.info('Acquisition stopped')
            self.acquisition_status.set_title('Acquisition stopped')
            self.acquisition_status.add_task('Error')
            self.acquisition_status.set_status('Error', 'l''username fornito non esiste', 'done')
            return
        except BadCredentialsException:
            error = True
            self.labelStatus.setText("Errore:\nLa password inserita è errata...")
            logger_acquisition.info('Errore: la password inserita è errata')
            logger_acquisition.info('Acquisition stopped')
            self.acquisition_status.set_title('Acquisition stopped')
            self.acquisition_status.add_task('Error')
            self.acquisition_status.set_status('Error', 'la password inserita è errata', 'done')
            return
        except ConnectionException:
            error = True
            self.labelStatus.setText("Errore:\nL'username o la password inseriti sono errati...")
            logger_acquisition.info('Errore: l''username o la password inseriti sono errati')
            logger_acquisition.info('Acquisition stopped')
            self.acquisition_status.set_title('Acquisition stopped')
            self.acquisition_status.add_task('Error')
            self.acquisition_status.set_status('Error', 'l''username o la password inseriti sono errati', 'done')
            return
        except ProfileNotExistsException:
            error = True
            self.labelStatus.setText("Errore:\nIl nome del profilo inserito non esiste...")
            logger_acquisition.info('Errore: il nome del profilo inserito non esiste')
            logger_acquisition.info('Acquisition stopped')
            self.acquisition_status.set_title('Acquisition stopped')
            self.acquisition_status.add_task('Error')
            self.acquisition_status.set_status('Error', 'il nome del profilo inserito non esiste', 'done')
            return

        if error:
            pass
        else:
            self.acquisition_status.add_task('Scraping')
            self.acquisition_status.set_status('Scraping', 'Started', 'done')
            if(self.checkBox_post.isChecked()):
                logger_acquisition.info('Scraping user''s posts')
                insta.scrape_post()
            self.progressBar.setValue(10)
            if(self.checkBox_2_followee.isChecked()):
                logger_acquisition.info('Scraping user''s followees')
                insta.scrape_followees()
            self.progressBar.setValue(20)
            if(self.checkBox_3_highlight.isChecked()):
                logger_acquisition.info('Scraping user''s highlights')
                insta.scrape_highlights()
            self.progressBar.setValue(30)
            if(self.checkBox_4_story.isChecked()):
                logger_acquisition.info('Scraping user''s stories')
                insta.scrape_stories()
            self.progressBar.setValue(40)
            if(self.checkBox_5_taggedPost.isChecked()):
                logger_acquisition.info('Scraping user''s tagged posts')
                insta.scrape_taggedPosts()
            self.progressBar.setValue(50)
            if(self.checkBox_6_savedPost.isChecked()):
                logger_acquisition.info('Scraping user''s saved posts')
                insta.scrape_savedPosts()
            self.progressBar.setValue(60)
            if(self.checkBox_7_follower.isChecked()):
                logger_acquisition.info('Scraping user''s followers')
                insta.scrape_followers()
            self.progressBar.setValue(70)
            logger_acquisition.info('Scraping user''s profile picture')
            insta.scrape_profilePicture()
            logger_acquisition.info('Scraping user''s info')
            insta.scrape_info()
            logger_acquisition.info('Acquisition end')
            ntp = utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])
            logger_acquisition.info(f'NTP end acquisition time: {ntp}')
            self.acquisition_status.set_title('Acquisition completed')
            instaZip = InstragramController(self.input_username.text(), self.input_password.text(),
                                            self.input_profile.text(), self.acquisition_directory)
            logger_acquisition.info('Creating zip files')
            instaZip.createZip(self.acquisition_directory)
            self.acquisition_status.add_task('Zip files')
            self.acquisition_status.set_status('Zip files', 'Creation completed', 'done')

            logger_acquisition.info('Creating main zip file')

            final_zip_name = ""+self.input_profile.text()+".zip"
            folder_path = self.acquisition_directory
            temp_zip_path = os.path.join(folder_path, "temp_zip.zip")
            with zipfile.ZipFile(final_zip_name, mode="w") as final_zip:
                for filename in os.listdir(folder_path):
                    folderToDelete = os.path.join(folder_path, filename)
                    if filename.endswith(".zip"):
                        if filename == final_zip_name:
                            pass
                        else:
                            shutil.copy(os.path.join(folder_path, filename), temp_zip_path)
                            final_zip.write(temp_zip_path, arcname=filename)
                            os.remove(temp_zip_path)
                            os.remove(folderToDelete)

            self.acquisition_status.add_task('Main zip file')
            self.acquisition_status.set_status('Main zip file', 'Creation completed', 'done')

            logger_acquisition.info('Calculate hash file')
            files = [f.name for f in os.scandir(self.acquisition_directory) if f.is_file()]

            for file in files:
                filename = os.path.join(self.acquisition_directory, file)
                if file != 'acquisition.hash':
                    file_stats = os.stat(filename)
                    logger_hashreport.info(file)
                    logger_hashreport.info('=========================================================')
                    logger_hashreport.info(f'Size: {file_stats.st_size}')
                    algorithm = 'md5'
                    logger_hashreport.info(f'MD5: {utility.calculate_hash(filename, algorithm)}')
                    algorithm = 'sha1'
                    logger_hashreport.info(f'SHA-1: {utility.calculate_hash(filename, algorithm)}')
                    algorithm = 'sha256'
                    logger_hashreport.info(f'SHA-256: {utility.calculate_hash(filename, algorithm)}\n')
            self.acquisition_status.add_task('Hash file')
            self.acquisition_status.set_status('Hash file', 'Hash file calculated', 'done')
            os.chdir(originalPath)
            logger_acquisition.info('PDF generation start')
            report = ReportController(self.acquisition_directory, self.case_info)
            report.generate_pdf('instagram', ntp)
            logger_acquisition.info('PDF generation end')
            self.acquisition_status.add_task('PDF generation')
            self.acquisition_status.set_status('PDF generation', 'PDF generated', 'done')

            ### generate timestamp for the report ###
            options = self.configuration_timestamp.options
            self.is_enabled_timestamp = options['enabled']
            if self.is_enabled_timestamp:
                self.timestamp = TimestampView()
                self.timestamp.set_options(options)
                self.timestamp.apply_timestamp(self.acquisition_directory, 'acquisition_report.pdf')


        self.progressBar.setValue(100)
        os.startfile(self.acquisition_directory)

    def onTextChanged(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.scrapeButton.setEnabled(all_field_filled)


