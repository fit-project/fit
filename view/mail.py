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



from PyQt5 import QtWidgets
from PyQt5.QtCore import QRegExp, QDate, Qt, QRect, QMetaObject, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator, QRegExpValidator, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QTreeWidget, QTreeWidgetItem

from view.acquisition.acquisition import Acquisition
from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView

from controller.mail import Mail as MailController

from common.settings import DEBUG
from common.config import LogConfigTools

from common.constants.view import mail, general
from common.constants.view.pec import search_pec

from common.constants import tasks, state, status, error, details as Details, logger as Logger

logger = logging.getLogger(__name__)


class Mail(QtWidgets.QMainWindow):
    stop_signal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        self.email_folder = None
        self.mail_controller = None
        self.input_email = None
        self.input_password = None
        self.input_server = None
        self.input_port = None
        self.input_from = None
        self.input_to = None
        self.input_subject = None
        self.input_from_date = None
        self.input_to_date = None
        self.acquisition_directory = None
        self.is_enabled_timestamp = False
        self.log_confing = LogConfigTools()
        self.case_info = None
        

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.width = 990
        self.height = 590
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.wizard = wizard

        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.setObjectName("email_scrape_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")

        # set font
        font = QFont()
        font.setPointSize(10)
        font.setFamily('Arial')

        # PROGRESS BAR
        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.progress_bar.setFixedHeight(25)
        self.status.addPermanentWidget(self.progress_bar)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.setStatusBar(self.status)
        self.progress_bar.setHidden(True)

        # IMAP GROUP
        self.imap_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.imap_group_box.setEnabled(True)
        self.imap_group_box.setGeometry(QRect(50, 20, 430, 200))
        self.imap_group_box.setObjectName("imap_group_box")

        # SCRAPED EMAILS TREE
        layout = QVBoxLayout()
        self.emails_tree = QTreeWidget(self.centralwidget)
        self.emails_tree.setGeometry(QRect(510, 25, 440, 470))
        self.emails_tree.setSelectionMode(QTreeWidget.NoSelection)
        self.emails_tree.itemChanged.connect(self.__on_item_changed)
        
        self.emails_tree.setObjectName("emails_tree")
        self.emails_tree.setFont(font)

        self.emails_tree.setHeaderLabel(mail.IMAP_FOUND_EMAILS)
        self.root = QTreeWidgetItem([mail.IMAP_FOLDERS])
        self.emails_tree.addTopLevelItem(self.root)
        layout.addWidget(self.emails_tree)

        # EMAIL FIELD
        self.input_email = QtWidgets.QLineEdit(self.centralwidget)
        self.input_email.setGeometry(QRect(180, 60, 240, 20))
        self.input_email.setFont(QFont('Arial', 10))
        self.input_email.setText('example@example.com')
        email_regex = QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")  # check
        validator = QRegExpValidator(email_regex)
        self.input_email.setValidator(validator)
        self.input_email.setObjectName("input_email")

        # PASSWORD FIELD
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QRect(180, 95, 240, 20))
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.setFont(QFont('Arial', 10))
        self.input_password.setText('password')
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # SERVER FIELD
        self.input_server = QtWidgets.QLineEdit(self.centralwidget)
        self.input_server.setGeometry(QRect(180, 130, 240, 20))
        self.input_server.setFont(QFont('Arial', 10))
        self.input_server.setText('imap.server.com')
        self.input_server.setObjectName("input_server")

        # PORT FIELD
        self.input_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_port.setGeometry(QRect(180, 165, 240, 20))
        self.input_port.setFont(QFont('Arial', 10))
        self.input_port.setText('993')
        validator = QDoubleValidator()
        self.input_port.setValidator(validator)
        self.input_port.setObjectName("input_port")

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_email, self.input_password, self.input_server, self.input_port]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        # EMAIL LABEL
        self.label_email = QtWidgets.QLabel(self.centralwidget)
        self.label_email.setGeometry(QRect(90, 60, 80, 20))
        self.label_email.setFont(font)
        self.label_email.setAlignment(Qt.AlignRight)
        self.label_email.setObjectName("label_email")

        # PASSWORD LABEL
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QRect(90, 95, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setAlignment(Qt.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER LABEL
        self.label_server = QtWidgets.QLabel(self.centralwidget)
        self.label_server.setGeometry(QRect(90, 130, 80, 20))
        self.label_server.setFont(font)
        self.label_server.setAlignment(Qt.AlignRight)
        self.label_server.setObjectName("label_server")

        # PORT LABEL
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setGeometry(QRect(90, 165, 80, 20))
        self.label_port.setFont(font)
        self.label_port.setAlignment(Qt.AlignRight)
        self.label_port.setObjectName("label_port")

        # SCRAPING CRITERIA
        self.criteria_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.criteria_group_box.setEnabled(True)
        self.criteria_group_box.setGeometry(QRect(50, 260, 430, 235))
        self.criteria_group_box.setObjectName("criteria_group_box")

        # SENDER FIELD
        self.input_from = QtWidgets.QLineEdit(self.centralwidget)
        self.input_from.setGeometry(QRect(180, 300, 240, 20))
        self.input_from.setFont(QFont('Arial', 10))
        self.input_from.setObjectName("input_sender")

        # RECIPIENT FIELD
        self.input_to = QtWidgets.QLineEdit(self.centralwidget)
        self.input_to.setGeometry(QRect(180, 335, 240, 20))
        self.input_to.setFont(QFont('Arial', 10))
        self.input_to.setObjectName("input_recipient")

        # SUBJECT FIELD
        self.input_subject = QtWidgets.QLineEdit(self.centralwidget)
        self.input_subject.setGeometry(QRect(180, 370, 240, 20))
        self.input_subject.setFont(QFont('Arial', 10))
        self.input_subject.setObjectName("input_subject")

        # FROM DATE FIELD
        self.input_from_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_from_date.setGeometry(QRect(180, 405, 240, 20))
        self.input_from_date.setFont(QFont('Arial', 10))
        self.input_from_date.setDate(QDate(1990, 1, 1))
        self.input_from_date.setObjectName("input_from_date")

        # TO DATE FIELD
        self.input_to_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_to_date.setGeometry(QRect(180, 440, 240, 20))
        self.input_to_date.setFont(QFont('Arial', 10))
        self.input_to_date.setDate(QDate.currentDate())
        self.input_to_date.setObjectName("input_to_date")

        # FROM LABEL
        self.label_from = QtWidgets.QLabel(self.centralwidget)
        self.label_from.setGeometry(QRect(90, 300, 80, 20))
        self.label_from.setFont(font)
        self.label_from.setAlignment(Qt.AlignRight)
        self.label_from.setObjectName("label_sender")

        # TO LABEL
        self.label_to = QtWidgets.QLabel(self.centralwidget)
        self.label_to.setGeometry(QRect(90, 335, 80, 20))
        self.label_to.setFont(font)
        self.label_to.setAlignment(Qt.AlignRight)
        self.label_to.setObjectName("label_recipient")

        # SUBJECT LABEL
        self.label_subject = QtWidgets.QLabel(self.centralwidget)
        self.label_subject.setGeometry(QRect(90, 370, 80, 20))
        self.label_subject.setFont(font)
        self.label_subject.setAlignment(Qt.AlignRight)
        self.label_subject.setObjectName("label_subject")

        # FROM DATE LABEL
        self.label_from_date = QtWidgets.QLabel(self.centralwidget)
        self.label_from_date.setGeometry(QRect(90, 405, 80, 20))
        self.label_from_date.setFont(font)
        self.label_from_date.setAlignment(Qt.AlignRight)
        self.label_from_date.setObjectName("label_from_date")

        # TO DATE LABEL
        self.label_to_date = QtWidgets.QLabel(self.centralwidget)
        self.label_to_date.setGeometry(QRect(90, 440, 80, 20))
        self.label_to_date.setFont(font)
        self.label_to_date.setAlignment(Qt.AlignRight)
        self.label_to_date.setObjectName("label_to_date")

        # LOGIN BUTTON
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setGeometry(QRect(405, 505, 75, 25))
        self.login_button.clicked.connect(self.__login)
        self.login_button.setFont(font)
        self.login_button.setObjectName("LoginAction")
        self.login_button.setEnabled(True)

        # SCRAPE BUTTON
        self.download_button = QtWidgets.QPushButton(self.centralwidget)
        self.download_button.setGeometry(QRect(875, 505, 75, 25))
        self.download_button.clicked.connect(self.__save_emails)
        self.download_button.setFont(font)
        self.download_button.setObjectName("StartAction")
        self.download_button.setEnabled(False)

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menu_configuration = QtWidgets.QAction("Configuration", self)
        self.menu_configuration.setObjectName("menuConfiguration")
        self.menu_configuration.triggered.connect(self.__configuration)
        self.menuBar().addAction(self.menu_configuration)

        # CASE BUTTON
        self.case_action = QtWidgets.QAction("Case", self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.__case)
        self.menuBar().addAction(self.case_action)

        # BACK ACTION
        back_action = QtWidgets.QAction("Back to wizard", self)
        back_action.setStatusTip("Go back to the main menu")
        back_action.triggered.connect(self.__back_to_wizard)
        self.menuBar().addAction(back_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")


        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QIcon(os.path.join('assets/svg/', 'FIT.svg')))

        # ACQUISITION
        self.acquisition = Acquisition(logger, self.progress_bar, self.status, self)


        self.acquisition_is_running = False
        self.start_acquisition_is_finished = False
        self.start_acquisition_is_started = False
        self.stop_acquisition_is_started = False


        # Enable/Disable other modules logger
        if not DEBUG:
            loggers = [logging.getLogger()]  # get the root logger
            loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict if
                                 name not in [__name__, 'hashreport']]

            self.log_confing.disable_loggers(loggers)

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.imap_group_box.setTitle(search_pec.SETTINGS)
        self.criteria_group_box.setTitle(search_pec.CRITERIA)
        self.label_email.setText(search_pec.LABEL_USERNAME)
        self.label_password.setText(search_pec.LABEL_PASSWORD)
        self.label_server.setText(search_pec.LABEL_IMAP_SERVER) 
        self.label_port.setText(search_pec.LABEL_IMAP_PORT)
        self.label_from.setText(search_pec.LABEL_FROM)
        self.label_to.setText(search_pec.LABEL_TO)
        self.label_subject.setText(search_pec.LABEL_SUBJECT)
        self.label_from_date.setText(search_pec.LABEL_FROM_DATE)
        self.label_to_date.setText(search_pec.LABEL_TO_DATE)
        self.login_button.setText(search_pec.LOGIN_BUTTON)
        self.download_button.setText(search_pec.DOWNLOAD_BUTTON)

    def __login(self):
        email = self.input_email.text()
        password = self.input_password.text()
        server = self.input_server.text()
        port = self.input_port.text()
        self.mail_controller = MailController()

        try:
            self.mail_controller.check_server(server, port)
        except Exception as e:  # WRONG SERVER
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  mail.SERVER_ERROR,
                                  error.SERVER_ERROR,
                                  str(e))
            error_dlg.exec_()

        try:
            self.mail_controller.check_login(email, password)
        except Exception as e:  # WRONG CREDENTIALS
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  mail.LOGIN_ERROR,
                                  error.LOGIN_ERROR,
                                  str(e))
            error_dlg.exec_()

        else:
            self.download_button.setEnabled(False)
            self.__start_dump_email()
            self.download_button.setEnabled(True)
            self.emails_tree.expandAll()

    def __start_dump_email(self):

        # Create acquisition directory
        self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
            'email',
            self.configuration_general.configuration['cases_folder_path'],
            self.case_info['name'],
            self.input_email.text()
        )
        if self.acquisition_directory is not None:
            self.start_acquisition_is_started = True

            
            # show progress bar
            self.progress_bar.setHidden(False)
            self.acquisition.start([], self.acquisition_directory, self.case_info, 1)


        # remove items from tree to clear the acquisition
        if self.email_folder is not None:
            while self.emails_tree.topLevelItemCount() > 0:
                item = self.emails_tree.takeTopLevelItem(0)
                del item
            self.root = QTreeWidgetItem([mail.IMAP_FOLDERS])
            self.emails_tree.setHeaderLabel(mail.IMAP_FOUND_EMAILS)
            self.emails_tree.addTopLevelItem(self.root)

        self.login_button.setEnabled(False)
        self.status.showMessage(Logger.FETCH_EMAILS)
        self.acquisition.logger.info(Logger.FETCH_EMAILS)
        self.acquisition.info.add_task(tasks.FETCH_EMAILS, state.STARTED, status.PENDING)

        self.setEnabled(False)
        self.__fetch_emails()


    def __fetch_emails(self):
        # converting date fields
        _from_date = self.input_from_date.date()  # qDate obj
        _to_date = self.input_to_date.date()  # qDate obj
        selected_from_date = _from_date.toPyDate()
        selected_to_date = _to_date.toPyDate()
        selected_to_date = selected_to_date + timedelta(days=1)  # to include today's email

        self.params = self.mail_controller.set_criteria(
            sender=self.input_from.text(),
            recipient=self.input_to.text(),
            subject=self.input_subject.text(),
            from_date=selected_from_date,
            to_date=selected_to_date)
        
        self.acquisition.logger.info(Logger.SEARCH_CRITERIA.format(self.params))
        emails = self.mail_controller.get_mails_from_every_folder(self.params)


        row = self.acquisition.info.get_row(tasks.FETCH_EMAILS)
        self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, '')
        self.acquisition.upadate_progress_bar()

        if emails is not None:
            for key in emails:
                self.email_folder = QTreeWidgetItem([key])
                self.email_folder.setData(0, Qt.UserRole, key)  # add identifier to the tree items
                self.email_folder.setCheckState(0, Qt.Unchecked)
                self.root.addChild(self.email_folder)

                for value in emails[key]:
                    sub_item = QTreeWidgetItem([value])
                    sub_item.setData(0, Qt.UserRole, key)
                    sub_item.setCheckState(0, Qt.Unchecked)
                    self.email_folder.addChild(sub_item)

            self.emails_tree.expandItem(self.root)  # expand root
        else:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  mail.NO_EMAILS,
                                  error.NO_EMAILS,
                                  Details.RETRY
                                  )

            error_dlg.buttonClicked.connect(quit)
        
        self.setEnabled(True)

        # hidden progress bar
        self.progress_bar.setHidden(True)
        self.status.showMessage('')
        
    def __on_item_changed(self, item, column):
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            child.setCheckState(column, item.checkState(column))

    def __on_text_changed(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_fields_filled)

    def __save_emails(self):
        emails_to_save = {}

        self.setEnabled(False)
        self.progress_bar.setHidden(False)
        self.status.showMessage(Logger.SAVE_EMAILS)
        self.acquisition.logger.info(Logger.SAVE_EMAILS)
        self.acquisition.info.add_task(tasks.SAVE_EMAILS, state.STARTED, status.PENDING)
        

        for i in range(self.root.childCount()):
            folder = self.root.child(i)
            folder_name = folder.text(0)
            for k in range(folder.childCount()):
                email = folder.child(k)

                if email.checkState(0) == Qt.CheckState.Checked:  
                    if folder_name in emails_to_save:
                        emails_to_save[folder_name].append(email.text(0))
                    else:
                        emails_to_save[folder_name] = [email.text(0)]
        
        if len(emails_to_save) > 0:
            # Create acquisition folder
            mail_dir = os.path.join(self.acquisition_directory, 'acquisition_mail')
            if not os.path.exists(mail_dir):
                os.makedirs(mail_dir)
            
            self.mail_controller.download_single_messages(mail_dir, emails_to_save)
            self.__zip_and_remove(mail_dir)
        
        row = self.acquisition.info.get_row(tasks.SAVE_EMAILS)
        self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, '')
        self.acquisition.upadate_progress_bar()

        self.acquisition.stop([], '', 1)
        self.acquisition.log_end_message()
      
        self.acquisition.post_acquisition.execute(self.acquisition_directory, self.case_info, 'email')
        self.setEnabled(True)
        self.login_button.setEnabled(True)

        # hidden progress bar
        self.progress_bar.setHidden(True)
        self.status.showMessage('')

        self.__show_finish_acquisition_dialog()

    def __zip_and_remove(self, mail_dir):

        shutil.make_archive(mail_dir, 'zip', mail_dir)

        try:
            shutil.rmtree(mail_dir)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  mail.SAVE_MAIL,
                                  error.SAVE_MAIL,
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.buttonClicked.connect(quit)

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.Yes:
            self.__open_acquisition_directory()

    def __open_acquisition_directory(self):
        os.startfile(self.acquisition_directory)

    def __case(self):
        self.case_view.exec_()

    def __configuration(self):
        self.configuration_view.exec_()

    def __back_to_wizard(self):
        self.deleteLater()
        self.wizard.reload_case_info()
        self.wizard.show()
