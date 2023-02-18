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
from datetime import timedelta

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp, QDate, Qt
from PyQt5.QtGui import QFont, QDoubleValidator, QRegExpValidator
from PyQt5.QtWidgets import QVBoxLayout, QTreeWidget, QTreeWidgetItem

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


class Mail(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        self.email_folder = None
        self.mail_controller = None
        self.input_email = None
        self.input_password = None
        self.input_server = None
        self.input_port = None
        self.input_sender = None
        self.input_recipient = None
        self.input_subject = None
        self.input_from_date = None
        self.input_to_date = None
        self.error_msg = ErrorMessage()
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.acquisition_status = AcquisitionStatusView(self)
        self.acquisition_status.setupUi()
        self.log_confing = LogConfigMail()

    def init(self, case_info):
        self.width = 990
        self.height = 590
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()

        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.setObjectName("email_scrape_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily('Arial')

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

        # IMAP GROUP
        self.imap_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.imap_group_box.setEnabled(True)
        self.imap_group_box.setGeometry(QtCore.QRect(50, 20, 430, 200))
        self.imap_group_box.setObjectName("imap_group_box")

        # SCRAPED EMAILS TREE
        layout = QVBoxLayout()
        self.emails_tree = QTreeWidget(self.centralwidget)
        self.emails_tree.setGeometry(QtCore.QRect(510, 25, 440, 470))
        self.emails_tree.setSelectionMode(QTreeWidget.MultiSelection)
        self.emails_tree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.emails_tree.setObjectName("emails_tree")
        self.emails_tree.setFont(font)

        self.emails_tree.setHeaderLabel("Email trovate")
        self.root = QTreeWidgetItem(["Cartelle"])
        self.emails_tree.addTopLevelItem(self.root)
        layout.addWidget(self.emails_tree)

        # EMAIL FIELD
        self.input_email = QtWidgets.QLineEdit(self.centralwidget)
        self.input_email.setGeometry(QtCore.QRect(180, 60, 240, 20))
        self.input_email.setFont(QFont('Arial', 10))
        self.input_email.setText('example@example.com')
        email_regex = QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")  # check
        validator = QRegExpValidator(email_regex)
        self.input_email.setValidator(validator)
        self.input_email.setObjectName("input_email")

        # PASSWORD FIELD
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(180, 95, 240, 20))
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.setFont(QFont('Arial', 10))
        self.input_password.setText('password')
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # SERVER FIELD
        self.input_server = QtWidgets.QLineEdit(self.centralwidget)
        self.input_server.setGeometry(QtCore.QRect(180, 130, 240, 20))
        self.input_server.setFont(QFont('Arial', 10))
        self.input_server.setText('imap.server.com')
        self.input_server.setObjectName("input_server")

        # PORT FIELD
        self.input_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_port.setGeometry(QtCore.QRect(180, 165, 240, 20))
        self.input_port.setFont(QFont('Arial', 10))
        self.input_port.setText('993')
        validator = QDoubleValidator()
        self.input_port.setValidator(validator)
        self.input_port.setObjectName("input_port")

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_email, self.input_password, self.input_server, self.input_port]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)


        # EMAIL LABEL
        self.label_email = QtWidgets.QLabel(self.centralwidget)
        self.label_email.setGeometry(QtCore.QRect(90, 60, 80, 20))
        self.label_email.setFont(font)
        self.label_email.setAlignment(QtCore.Qt.AlignRight)
        self.label_email.setObjectName("label_email")

        # PASSWORD LABEL
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(90, 95, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setAlignment(QtCore.Qt.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER LABEL
        self.label_server = QtWidgets.QLabel(self.centralwidget)
        self.label_server.setGeometry(QtCore.QRect(90, 130, 80, 20))
        self.label_server.setFont(font)
        self.label_server.setAlignment(QtCore.Qt.AlignRight)
        self.label_server.setObjectName("label_server")

        # PORT LABEL
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setGeometry(QtCore.QRect(90, 165, 80, 20))
        self.label_port.setFont(font)
        self.label_port.setAlignment(QtCore.Qt.AlignRight)
        self.label_port.setObjectName("label_port")

        # SCRAPING CRITERIA
        self.criteria_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.criteria_group_box.setEnabled(True)
        self.criteria_group_box.setGeometry(QtCore.QRect(50, 260, 430, 235))
        self.criteria_group_box.setObjectName("criteria_group_box")

        # SENDER FIELD
        self.input_sender = QtWidgets.QLineEdit(self.centralwidget)
        self.input_sender.setGeometry(QtCore.QRect(180, 300, 240, 20))
        self.input_sender.setFont(QFont('Arial', 10))
        self.input_sender.setObjectName("input_sender")

        # RECIPIENT FIELD
        self.input_recipient = QtWidgets.QLineEdit(self.centralwidget)
        self.input_recipient.setGeometry(QtCore.QRect(180, 335, 240, 20))
        self.input_recipient.setFont(QFont('Arial', 10))
        self.input_recipient.setObjectName("input_recipient")

        # SUBJECT FIELD
        self.input_subject = QtWidgets.QLineEdit(self.centralwidget)
        self.input_subject.setGeometry(QtCore.QRect(180, 370, 240, 20))
        self.input_subject.setFont(QFont('Arial', 10))
        self.input_subject.setObjectName("input_subject")

        # FROM DATE FIELD
        self.input_from_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_from_date.setGeometry(QtCore.QRect(180, 405, 240, 20))
        self.input_from_date.setFont(QFont('Arial', 10))
        self.input_from_date.setDate(QDate(1990, 1, 1))
        self.input_from_date.setObjectName("input_from_date")

        # TO DATE FIELD
        self.input_to_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_to_date.setGeometry(QtCore.QRect(180, 440, 240, 20))
        self.input_to_date.setFont(QFont('Arial', 10))
        self.input_to_date.setDate(QDate.currentDate())
        self.input_to_date.setObjectName("input_to_date")

        # SENDER LABEL
        self.label_sender = QtWidgets.QLabel(self.centralwidget)
        self.label_sender.setGeometry(QtCore.QRect(90, 300, 80, 20))
        self.label_sender.setFont(font)
        self.label_sender.setAlignment(QtCore.Qt.AlignRight)
        self.label_sender.setObjectName("label_sender")

        # RECIPIENT LABEL
        self.label_recipient = QtWidgets.QLabel(self.centralwidget)
        self.label_recipient.setGeometry(QtCore.QRect(90, 335, 80, 20))
        self.label_recipient.setFont(font)
        self.label_recipient.setAlignment(QtCore.Qt.AlignRight)
        self.label_recipient.setObjectName("label_recipient")

        # SUBJECT LABEL
        self.label_subject = QtWidgets.QLabel(self.centralwidget)
        self.label_subject.setGeometry(QtCore.QRect(90, 370, 80, 20))
        self.label_subject.setFont(font)
        self.label_subject.setAlignment(QtCore.Qt.AlignRight)
        self.label_subject.setObjectName("label_subject")

        # FROM DATE LABEL
        self.label_from_date = QtWidgets.QLabel(self.centralwidget)
        self.label_from_date.setGeometry(QtCore.QRect(90, 405, 80, 20))
        self.label_from_date.setFont(font)
        self.label_from_date.setAlignment(QtCore.Qt.AlignRight)
        self.label_from_date.setObjectName("label_from_date")

        # TO DATE LABEL
        self.label_to_date = QtWidgets.QLabel(self.centralwidget)
        self.label_to_date.setGeometry(QtCore.QRect(90, 440, 80, 20))
        self.label_to_date.setFont(font)
        self.label_to_date.setAlignment(QtCore.Qt.AlignRight)
        self.label_to_date.setObjectName("label_to_date")

        # LOGIN BUTTON
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setGeometry(QtCore.QRect(405, 505, 75, 25))
        self.login_button.clicked.connect(self.login)
        self.login_button.setFont(font)
        self.login_button.setObjectName("StartAcquisitionAction")
        self.login_button.setEnabled(True)

        # SCRAPE BUTTON
        self.scrape_button = QtWidgets.QPushButton(self.centralwidget)
        self.scrape_button.setGeometry(QtCore.QRect(875, 505, 75, 25))
        self.scrape_button.clicked.connect(self.save_messages)
        self.scrape_button.setFont(font)
        self.scrape_button.setObjectName("StartAction")
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

         #Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox, 'group_box_network_check')

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
        self.imap_group_box.setTitle(_translate("email_scrape_window", "Impostazioni server IMAP"))
        self.criteria_group_box.setTitle(_translate("email_scrape_window", "Criteri di ricerca"))
        self.label_email.setText(_translate("email_scrape_window", "E-mail*"))
        self.label_password.setText(_translate("email_scrape_window", "Password*"))
        self.label_server.setText(_translate("email_scrape_window", "Server IMAP*"))
        self.label_port.setText(_translate("email_scrape_window", "Port*"))
        self.label_sender.setText(_translate("email_scrape_window", "Mittente"))
        self.label_recipient.setText(_translate("email_scrape_window", "Destinatario"))
        self.label_subject.setText(_translate("email_scrape_window", "Oggetto"))
        self.label_from_date.setText(_translate("email_scrape_window", "Data di inizio"))
        self.label_to_date.setText(_translate("email_scrape_window", "Data di fine"))
        self.login_button.setText(_translate("email_scrape_window", "Fetch"))
        self.scrape_button.setText(_translate("email_scrape_window", "Download"))

    def login(self):
        email = self.input_email.text()
        password = self.input_password.text()
        server = self.input_server.text()
        port = self.input_port.text()
        self.mail_controller = MailController()

        try:
            self.mail_controller.check_server(server, port)
        except Exception as e:  # WRONG SERVER
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  self.error_msg.TITLES['server_error'],
                                  self.error_msg.MESSAGES['server_error'],
                                  "Please retry.")
            error_dlg.exec_()
            return

        try:
            self.mail_controller.check_login(email, password)
        except Exception as e:  # WRONG CREDENTIALS
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  self.error_msg.TITLES['login_error'],
                                  self.error_msg.MESSAGES['login_error'],
                                  "Please retry.")
            error_dlg.exec_()
            return

        else:
            self.start_dump_email()
            self.scrape_button.setEnabled(True)
            self.emails_tree.expandAll()

    def start_dump_email(self):

        # Create acquisition directory
        self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
            'email',
            self.configuration_general.configuration['cases_folder_path'],
            self.case_info['name'],
            self.input_email.text()
        )
        if self.acquisition_directory is not None:
            if not os.path.exists(os.path.join(self.acquisition_directory, 'acquisition')):
                os.makedirs(os.path.join(self.acquisition_directory, 'acquisition'))
            # show progress bar
            self.progress_bar.setHidden(False)
            self.progress_bar.setValue(10)
            self.acquisition_is_started = True
            self.acquisition_status.set_title('Acquisition in progress:')
            self.acquisition_status.add_task('Case Folder')
            self.acquisition_status.set_status('Case Folder', self.acquisition_directory, 'done')
            self.status.showMessage(self.acquisition_directory)
            self.progress_bar.setValue(25)

            # Step 3: Create loggin handler and start loggin information
            self.log_confing.change_filehandlers_path(self.acquisition_directory)
            logging.config.dictConfig(self.log_confing.config)
            self.progress_bar.setValue(50)
            logger_acquisition.info('Login started')
            logger_acquisition.info(
                f'NTP start acquisition time: {utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])}')
            self.progress_bar.setValue(75)
            
            self.acquisition_status.add_task('Logger')
            self.acquisition_status.set_status('Logger', 'Started', 'done')
            self.status.showMessage('Logging handler and login information have been started')
            self.progress_bar.setValue(90)

            self.acquisition_status.set_title('Login started success:')

        # remove items from tree to clear the acquisition
        if self.email_folder is not None:
            while self.emails_tree.topLevelItemCount() > 0:
                item = self.emails_tree.takeTopLevelItem(0)
                del item
            self.root = QTreeWidgetItem(["Cartelle"])
            self.emails_tree.setHeaderLabel("Email trovate")
            self.emails_tree.addTopLevelItem(self.root)

        # Step 1: Disable start_acquisition_action and clear current threads and acquisition information on dialog
        action = self.findChild(QtWidgets.QAction, 'StartAcquisitionAction')
        self.progress_bar.setValue(50)
        if action is not None:
            action.setEnabled(False)
        self.acquisition_status.clear()
        self.acquisition_status.set_title('Acquisition is started!')
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
                
        if self.acquisition_is_started:
            self.setEnabled(False)
            self.acquisition_status.clear()
            self.progress_bar.setValue(100)
            self.acquisition_status.set_title('Login success:')
            self.acquisition_status.add_task('Login')
            self.acquisition_status.set_status('Login', 'Completed', 'done')
            logger_acquisition.info('Login completed')
            self.status.showMessage('Login compleded')
            self.progress_bar.setHidden(True)
            self.get_messages()
            self.setEnabled(True)

    def _acquisition_status(self):
        self.acquisition_status.show()

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_fields_filled)

    def get_messages(self):
        # converting date fields
        _from_date = self.input_from_date.date()  # qDate obj
        _to_date = self.input_to_date.date()  # qDate obj
        selected_from_date = _from_date.toPyDate()
        selected_to_date = _to_date.toPyDate()
        selected_to_date = selected_to_date + timedelta(days=1)  # to include today's email

        self.params = self.mail_controller.set_criteria(
            sender=self.input_sender.text(),
            recipient=self.input_recipient.text(),
            subject=self.input_subject.text(),
            from_date=selected_from_date,
            to_date=selected_to_date)

        self.acquisition_status.set_title('Params acquisition:')
        self.acquisition_status.add_task('Params')
        self.acquisition_status.set_status('Params', 'acquisition completed', 'done')
        logger_acquisition.info('Params acquisition completed')
        self.status.showMessage('Params acquisition compleded')
        emails = self.mail_controller.get_mails_from_every_folder(self.params)
        for key in emails:
            self.email_folder = QTreeWidgetItem([key])
            self.email_folder.setData(0, Qt.UserRole, key)  # add identifier to the tree items
            self.root.addChild(self.email_folder)

            for value in emails[key]:
                sub_item = QTreeWidgetItem([value])
                sub_item.setData(0, Qt.UserRole, key)
                self.email_folder.addChild(sub_item)

        self.emails_tree.expandItem(self.root)  # expand root folder

        return

    def save_messages(self):
        self.setEnabled(False)
        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(10)
        logger_acquisition.info('Save emails started')
        self.status.showMessage('Save emails started')
        self.progress_bar.setValue(20)

        emails_dict = {}
        folders_list = []
        selected_items = self.emails_tree.selectedItems()
        for items in selected_items:
            if items.text(0) == 'Cartelle':
                # scrape everything anyway (even is single messages are selected)
                self.mail_controller.download_everything(self.acquisition_directory)
                self.save_info()
                return
        self.progress_bar.setValue(30)

        for folders in selected_items:
            if folders.childCount()>0:
                # scrape every selected folder anyway (even is single messages are selected)
                folders_list.append(folders.data(0, Qt.UserRole))
        if len(folders_list) > 0:
            self.mail_controller.download_messages(folders_list, self.acquisition_directory)
            self.progress_bar.setValue(50)
            self.save_info()

            return

        for selected_email in selected_items:
            folder_email = selected_email.data(0, Qt.UserRole)

            if folder_email in emails_dict:  # add folder and email to the dict
                emails_dict[folder_email].append(selected_email.text(0))
            else:
                emails_dict[folder_email] = [selected_email.text(0)]

        self.mail_controller.download_single_messages(self.acquisition_directory, emails_dict)
        self.progress_bar.setValue(50)
        self.save_info()
        return

    def save_info(self):
        self.progress_bar.setValue(70)
        self.acquisition_status.set_title('Save emails:')
        self.acquisition_status.add_task('Save emails')
        self.acquisition_status.set_status('Save emails', 'completed', 'done')
        logger_acquisition.info('Save emails completed')
        self.status.showMessage('Save emails compleded')

        project_name = "acquisition"
        acquisition_folder = os.path.join(self.acquisition_directory,project_name)
        if not os.path.exists(acquisition_folder):
            os.makedirs(acquisition_folder)
        # zipping email acquisition folder
        acquisition_emails_folder = os.path.join(self.acquisition_directory, project_name)
        zip_folder = shutil.make_archive(acquisition_emails_folder, 'zip', acquisition_emails_folder)
        self.acquisition_status.set_status('Save email', zip_folder, 'done')
        self.progress_bar.setValue(90)
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

        ### Waiting everything is synchronized
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(2000, loop.quit)
        loop.exec_()


        # Calculate acquisition hash
        self.status.showMessage('Calculate acquisition file hash')
        self.progress_bar.setValue(100)
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
        self.progress_bar.setValue(100)

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
        return

    def on_item_selection_changed(self):
        selected_items = self.emails_tree.selectedItems()
        for item in selected_items:
            self.update_child_items(item, item.isSelected())

    def update_child_items(self, item, selected):
        child_count = item.childCount()
        for i in range(child_count):
            child_item = item.child(i)
            child_item.setSelected(selected)
            self.update_child_items(child_item, selected)