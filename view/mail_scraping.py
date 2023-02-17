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
import os
import logging
import logging.config
import shutil

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator

from controller.mail import Mail as MailController
from controller.report import Report as ReportController

from view.acquisitionstatus import AcquisitionStatus as AcquisitionStatusView

from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView

from common.error import ErrorMessage

from common.settings import DEBUG
from common.config import LogConfigMail
import common.utility as utility

logger_acquisition = logging.getLogger(__name__)
logger_hashreport = logging.getLogger('hashreport')



class MailScraping(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

    def __init__(self, *args, **kwargs):
        super(MailScraping, self).__init__(*args, **kwargs)
        self.mail_controller = None
        self.input_sender = None
        self.input_subject = None
        self.input_from_date = None
        self.input_to_date = None
        self.error_msg = ErrorMessage()
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.acquisition_status = AcquisitionStatusView(self)
        self.acquisition_status.setupUi()
        self.log_confing = LogConfigMail()

    def init(self, case_info, mail_controller):
        self.width = 520
        self.height = 330
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.mail_controller = mail_controller
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()

        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.setObjectName("email_scrape_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")

        # PROGRESS BAR
        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.progress_bar.setFixedHeight(25)
        self.status.addPermanentWidget(self.progress_bar)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.setStatusBar(self.status)
        self.progress_bar.setHidden(True)

        '''# IMAP GROUP
        self.imap_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.imap_group_box.setEnabled(True)
        self.imap_group_box.setGeometry(QtCore.QRect(50, 20, 430, 240))
        self.imap_group_box.setObjectName("imap_group_box")'''

        # SENDER FIELD
        self.input_sender = QtWidgets.QLineEdit(self.centralwidget)
        self.input_sender.setGeometry(QtCore.QRect(180, 60, 240, 20))
        self.input_sender.setFont(QFont('Arial', 10))
        email_regex = QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")  # force email address
        validator = QRegExpValidator(email_regex)
        self.input_sender.setValidator(validator)
        self.input_sender.setObjectName("input_sender")

        # SUBJECT FIELD
        self.input_subject = QtWidgets.QLineEdit(self.centralwidget)
        self.input_subject.setGeometry(QtCore.QRect(180, 95, 240, 20))
        self.input_subject.setFont(QFont('Arial', 10))
        self.input_subject.setObjectName("input_subject")

        # FROM DATE FIELD
        self.input_from_date = QtWidgets.QLineEdit(self.centralwidget)
        self.input_from_date.setGeometry(QtCore.QRect(180, 130, 240, 20))
        self.input_from_date.setFont(QFont('Arial', 10))
        self.input_from_date.setObjectName("input_from_date")

        # to DATE FIELD
        self.input_to_date = QtWidgets.QLineEdit(self.centralwidget)
        self.input_to_date.setGeometry(QtCore.QRect(180, 165, 240, 20))
        self.input_to_date.setFont(QFont('Arial', 10))
        self.input_to_date.setObjectName("input_to_date")

        '''# DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_sender, self.input_subject, self.input_from_date, self.input_to_date]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)'''

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily('Arial')

        # SENDER LABEL
        self.label_sender = QtWidgets.QLabel(self.centralwidget)
        self.label_sender.setGeometry(QtCore.QRect(90, 60, 80, 20))
        self.label_sender.setFont(font)
        self.label_sender.setAlignment(QtCore.Qt.AlignRight)
        self.label_sender.setObjectName("label_sender")

        # SUBJECT LABEL
        self.label_subject = QtWidgets.QLabel(self.centralwidget)
        self.label_subject.setGeometry(QtCore.QRect(90, 95, 80, 20))
        self.label_subject.setFont(font)
        self.label_subject.setAlignment(QtCore.Qt.AlignRight)
        self.label_subject.setObjectName("label_subject")

        # FROM DATE LABEL
        self.label_from_date = QtWidgets.QLabel(self.centralwidget)
        self.label_from_date.setGeometry(QtCore.QRect(90, 130, 80, 20))
        self.label_from_date.setFont(font)
        self.label_from_date.setAlignment(QtCore.Qt.AlignRight)
        self.label_from_date.setObjectName("label_from_date")

        # TO DATE LABEL
        self.label_to_date = QtWidgets.QLabel(self.centralwidget)
        self.label_to_date.setGeometry(QtCore.QRect(90, 165, 80, 20))
        self.label_to_date.setFont(font)
        self.label_to_date.setAlignment(QtCore.Qt.AlignRight)
        self.label_to_date.setObjectName("label_to_date")

        # SCRAPE BUTTON
        self.scrape_button = QtWidgets.QPushButton(self.centralwidget)
        self.scrape_button.setGeometry(QtCore.QRect(345, 210, 75, 25))
        self.scrape_button.clicked.connect(self.start_dump_email)
        self.scrape_button.setFont(font)
        self.scrape_button.setObjectName("StartAcquisitionAction")
        self.scrape_button.setEnabled(False)

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

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
        # Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

        # Enable/Disable other modules logger
        if not DEBUG:
            loggers = [logging.getLogger()]  # get the root logger
            loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict if
                                 name not in [__name__, 'hashreport']]

            self.log_confing.disable_loggers(loggers)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("email_scrape_window", "Freezing Internet Tool"))
        '''self.imap_group_box.setTitle(
            _translate("email_scrape_window", "Impostazioni server IMAP"))'''
        self.label_sender.setText(_translate("email_scrape_window", "Mittente"))
        self.label_subject.setText(_translate("email_scrape_window", "Oggetto"))
        self.label_from_date.setText(_translate("email_scrape_window", "Data di inizio"))
        self.label_to_date.setText(_translate("email_scrape_window", "Data di fine"))
        self.scrape_button.setText(_translate("email_scrape_window", "Download"))

    def start_dump_email(self):
        # Step 1: Disable start_acquisition_action and clear current threads and acquisition information on dialog
        action = self.findChild(QtWidgets.QAction, 'StartAcquisitionAction')
        self.progress_bar.setValue(50)
        if action is not None:
            action.setEnabled(False)

        self.acquisition_status.clear()
        self.acquisition_status.set_title('Acquisition is started!')

        # Step 2: Create acquisition directory
        self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
            'email',
            self.configuration_general.configuration['cases_folder_path'],
            self.case_info['name'],
            self.input_sender.text()
        )
        if self.acquisition_directory is not None:

            # show progress bar
            self.progress_bar.setHidden(False)

            self.acquisition_is_started = True
            self.acquisition_status.set_title('Acquisition in progress:')
            self.acquisition_status.add_task('Case Folder')
            self.acquisition_status.set_status('Case Folder', self.acquisition_directory, 'done')
            self.status.showMessage(self.acquisition_directory)
            self.progress_bar.setValue(25)

            # Step 3: Create loggin handler and start loggin information
            self.log_confing.change_filehandlers_path(self.acquisition_directory)
            logging.config.dictConfig(self.log_confing.config)

            logger_acquisition.info('Acquisition started')
            logger_acquisition.info(
                f'NTP start acquisition time: {utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])}')

            self.acquisition_status.add_task('Logger')
            self.acquisition_status.set_status('Logger', 'Started', 'done')
            self.status.showMessage('Logging handler and login information have been started')
            self.progress_bar.setValue(50)

            self.acquisition_status.set_title('Acquisition started success:')

            # hidden progress bar
            # self.progress_bar.setHidden(True)
            # self.status.showMessage('')
            if self.acquisition_is_started:
                self.progress_bar.setHidden(False)

                # Step 1: Disable all actions and clear current acquisition information on dialog
                self.setEnabled(False)
                self.acquisition_status.clear()
                self.acquisition_status.set_title('Interruption of the acquisition in progress:')
                logger_acquisition.info('Acquisition stopped')
                logger_acquisition.info('Email scraping complete')
                # self.statusBar().showMessage('Message in statusbar.')


                # Step 4:  Save all resources
                self.status.showMessage('Save all resources')
                self.progress_bar.setValue(20)
                self.save_messages()

                logger_acquisition.info('Save all resource')
                self.acquisition_status.add_task('Save email')

                ### Waiting everything is synchronized
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(2000, loop.quit)
                loop.exec_()



                self.status.showMessage('Calculate acquisition file hash')
                self.progress_bar.setValue(100)

                # Step 5:  Calculate acquisition hash
                logger_acquisition.info('Calculate acquisition file hash')
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
                        logger_hashreport.info(f'SHA-256: {utility.calculate_hash(filename, algorithm)}')
                logger_acquisition.info('Acquisition end')

                ntp = utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])
                logger_acquisition.info(f'NTP end acquisition time: {ntp}')

                logger_acquisition.info('PDF generation start')
                ### generate pdf report ###
                report = ReportController(self.acquisition_directory, self.case_info)
                report.generate_pdf('email', ntp)
                logger_acquisition.info('PDF generation end')


                #### open the acquisition folder ####
                os.startfile(self.acquisition_directory)

                #### Enable all action ####
                self.setEnabled(True)
                action = self.findChild(QtWidgets.QAction, 'StartAcquisitionAction')

                # Enable start_acquisition_action
                if action is not None:
                    action.setEnabled(True)

                self.acquisition_is_started = False

                # hidden progress bar
                self.progress_bar.setHidden(True)
                self.status.showMessage('')

    def _acquisition_status(self):
        self.acquisition_status.show()

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.scrape_button.setEnabled(all_fields_filled)

    def save_messages(self):
        sender = self.input_sender.text()
        subject = self.input_subject.text()
        from_date= self.input_from_date.text()
        to_date = self.input_from_to.text()
        self.mail_controller.set_criteria(self.acquisition_directory, sender=sender,
                                          subject=subject, from_date=from_date, to_date=to_date)

        project_name = "acquisition"
        # zipping email acquisition folder
        acquisition_emails_folder = os.path.join(self.acquisition_directory, project_name)
        zip_folder = shutil.make_archive(acquisition_emails_folder,'zip', acquisition_emails_folder)
        self.acquisition_status.set_status('Save email', zip_folder, 'done')

        try:
            # removing unused acquisition folder
            shutil.rmtree(acquisition_emails_folder)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['save_mail'],
                                  self.error_msg.MESSAGES['save_mail'],
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.buttonClicked.connect(quit)
            error_dlg.exec_()

        return
