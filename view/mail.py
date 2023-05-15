#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import os
import re
import logging
import shutil
from datetime import timedelta

from PyQt5 import QtWidgets
from PyQt5.QtCore import (QObject, QThread, QRegExp, QDate, Qt, QRect, QMetaObject,
                           pyqtSignal, QEventLoop, QTimer, pyqtSlot)
from PyQt5.QtGui import QFont, QDoubleValidator, QRegExpValidator, QIcon


from view.acquisition.acquisition import Acquisition
from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView
from view.spinner import Spinner

from controller.mail import Mail as MailController

from common.constants.view import mail, general
from common.constants.view.pec import search_pec

from common.constants import tasks, error, details as Details, logger as Logger

logger = logging.getLogger(__name__)


class MailWorker(QObject):

    get_emails = pyqtSignal(dict)
    download = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, mail_controller, email, password, server, 
                 port, criteria, acquisition_mail_dir, emails_to_save, is_downloading):
        super().__init__()
        self.mail_controller = mail_controller       
        self.email = email
        self.password = password
        self.server = server
        self.port = port
        self.search_criteria = criteria
        self.acquisition_mail_dir = acquisition_mail_dir
        self.emails_to_save = emails_to_save
        self.is_downloading = is_downloading  
    
    @pyqtSlot()
    def run(self):
        try:
            if self.mail_controller.mailbox is None:
                self.mail_controller.check_server(self.server, self.port)

            if self.mail_controller.is_logged_in is False:
                self.mail_controller.check_login(self.email, self.password)

            if self.is_downloading is False:
                emails = self.mail_controller.get_mails_from_every_folder(self.search_criteria)
            else:
                self.__download_emails()

        except Exception as e: #Check Server
            self.error.emit({'title':mail.SERVER_ERROR, 'msg':error.MAIL_SERVER_ERROR, 'details':e})
        except Exception as e: #Check Login
            self.error.emit({'title':mail.LOGIN_ERROR, 'msg':error.LOGIN_ERROR, 'details':e})
        except Exception as e: #Get mails
            self.error.emit(e)
        except Exception as e: #Save mails
            self.error.emit(e)
        else:
            if self.is_downloading is False:
                self.get_emails.emit(emails)
            else:
                self.download.emit()
        finally:
            self.finished.emit()
    
    def __download_emails(self):
        for folder, emails_list in self.emails_to_save.items():
            for emails in emails_list:
                email_id = emails.partition('UID: ')[2]
                # Create acquisition folder
                folder_stripped = re.sub(r"[^a-zA-Z0-9]+", '-', folder)
                self.mail_controller.write_emails(email_id, self.acquisition_mail_dir, folder_stripped, folder)
                self.progress.emit()



class Mail(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        self.email = None
        self.password = None
        self.server = None
        self.port = None
        self.from_email = None
        self.to_email = None
        self.subject = None
        self.from_date = None
        self.to_date = None
        self.search_criteria = None
        self.acquisition_mail_dir = None
        self.folder_tree = None
        self.emails_to_save = None
        self.is_downloading = False
        self.increment = 0
        self.mail_controller = MailController()
        self.spinner = Spinner()
        self.acquisition_directory = None
        self.case_info = None
        self.email_validator = QRegExpValidator(QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"))
        self.is_valid_email = False
        self.emails_to_validate = []
        
          

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

        # CONFIGURATION GROUP BOX
        self.configuration_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.configuration_group_box.setEnabled(True)
        self.configuration_group_box.setGeometry(QRect(50, 20, 430, 200))
        self.configuration_group_box.setObjectName("configuration_group_box")

        # SCRAPED EMAILS TREE
        layout = QtWidgets.QVBoxLayout()
        self.emails_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.emails_tree.setGeometry(QRect(510, 25, 440, 470))
        self.emails_tree.setSelectionMode(QtWidgets.QTreeWidget.NoSelection)
        self.emails_tree.itemChanged.connect(self.__on_item_changed)
        
        self.emails_tree.setObjectName("emails_tree")
        self.emails_tree.setFont(font)

        self.emails_tree.setHeaderLabel(mail.IMAP_FOUND_EMAILS)
        self.root = QtWidgets.QTreeWidgetItem([mail.IMAP_FOLDERS])
        self.emails_tree.addTopLevelItem(self.root)
        layout.addWidget(self.emails_tree)

        # EMAIL FIELD
        self.input_email = QtWidgets.QLineEdit(self.configuration_group_box)
        self.input_email.setGeometry(QRect(130, 60, 240, 20))
        self.input_email.setFont(QFont('Arial', 10))
        self.input_email.setPlaceholderText(search_pec.PLACEHOLDER_USERNAME)
        self.input_email.setObjectName("input_email")
        self.emails_to_validate.append(self.input_email.objectName())

        # EMAIL LABEL
        self.label_email = QtWidgets.QLabel(self.configuration_group_box)
        self.label_email.setGeometry(QRect(40, 60, 80, 20))
        self.label_email.setFont(font)
        self.label_email.setAlignment(Qt.AlignRight)
        self.label_email.setObjectName("label_email")
        

        # PASSWORD FIELD
        self.input_password = QtWidgets.QLineEdit(self.configuration_group_box)
        self.input_password.setGeometry(QRect(130, 95, 240, 20))
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.setFont(QFont('Arial', 10))
        self.input_password.setPlaceholderText(search_pec.PLACEHOLDER_PASSWORD)
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # SERVER FIELD
        self.input_server = QtWidgets.QLineEdit(self.configuration_group_box)
        self.input_server.setGeometry(QRect(130, 130, 240, 20))
        self.input_server.setFont(QFont('Arial', 10))
        self.input_server.setPlaceholderText(search_pec.PLACEHOLDER_IMAP_SERVER)
        self.input_server.setObjectName("input_server")

        # PORT FIELD
        self.input_port = QtWidgets.QLineEdit(self.configuration_group_box)
        self.input_port.setGeometry(QRect(130, 165, 240, 20))
        self.input_port.setFont(QFont('Arial', 10))
        self.input_port.setPlaceholderText(search_pec.PLACEHOLDER_IMAP_PORT)
        validator = QDoubleValidator()
        self.input_port.setValidator(validator)
        self.input_port.setObjectName("input_port")

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_email, self.input_password, self.input_server, self.input_port]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        

        # PASSWORD LABEL
        self.label_password = QtWidgets.QLabel(self.configuration_group_box)
        self.label_password.setGeometry(QRect(40, 95, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setAlignment(Qt.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER LABEL
        self.label_server = QtWidgets.QLabel(self.configuration_group_box)
        self.label_server.setGeometry(QRect(40, 130, 80, 20))
        self.label_server.setFont(font)
        self.label_server.setAlignment(Qt.AlignRight)
        self.label_server.setObjectName("label_server")

        # PORT LABEL
        self.label_port = QtWidgets.QLabel(self.configuration_group_box)
        self.label_port.setGeometry(QRect(40, 165, 80, 20))
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
        self.input_from.setPlaceholderText(search_pec.PLACEHOLDER_FROM)

        self.input_from.textChanged.connect(self.__on_text_changed)
        self.input_from.editingFinished.connect(self.__on_editing_finished)
        self.emails_to_validate.append(self.input_from.objectName())

        # RECIPIENT FIELD
        self.input_to = QtWidgets.QLineEdit(self.centralwidget)
        self.input_to.setGeometry(QRect(180, 335, 240, 20))
        self.input_to.setFont(QFont('Arial', 10))
        self.input_to.setObjectName("input_recipient")
        self.input_to.setPlaceholderText(search_pec.PLACEHOLDER_TO)
        self.input_to.editingFinished.connect(self.__on_editing_finished)
        self.input_to.textChanged.connect(self.__on_text_changed)
        self.emails_to_validate.append(self.input_to.objectName())

        # SUBJECT FIELD
        self.input_subject = QtWidgets.QLineEdit(self.centralwidget)
        self.input_subject.setGeometry(QRect(180, 370, 240, 20))
        self.input_subject.setFont(QFont('Arial', 10))
        self.input_subject.setObjectName("input_subject")
        self.input_subject.setPlaceholderText(search_pec.PLACEHOLDER_SUBJECT)

        # FROM DATE FIELD
        self.input_from_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_from_date.setGeometry(QRect(180, 405, 240, 20))
        self.input_from_date.setFont(QFont('Arial', 10))
        self.input_from_date.setDate(QDate.currentDate())
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
        self.search_button = QtWidgets.QPushButton(self.centralwidget)
        self.search_button.setGeometry(QRect(405, 505, 75, 25))
        self.search_button.clicked.connect(self.__search)
        self.search_button.setFont(font)
        self.search_button.setObjectName("search_action")
        self.search_button.setEnabled(False)

        # SCRAPE BUTTON
        self.download_button = QtWidgets.QPushButton(self.centralwidget)
        self.download_button.setGeometry(QRect(875, 505, 75, 25))
        self.download_button.clicked.connect(self.__download)
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

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")


        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QIcon(os.path.join('assets/svg/', 'FIT.svg')))

        # ACQUISITION
        self.acquisition = Acquisition(logger, self.progress_bar, self.status, self)
        self.acquisition.post_acquisition.finished.connect(self.__are_post_acquisition_finished)
        self.is_first_acquisition_completed = False
        self.is_acquisition_running = False
      


    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.configuration_group_box.setTitle(search_pec.SETTINGS)
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
        self.search_button.setText(search_pec.SEARCH_BUTTON)
        self.download_button.setText(search_pec.DOWNLOAD_BUTTON)

    def __init_worker(self):
        self.thread_worker= QThread()
        self.worker = MailWorker(self.mail_controller, self.email, self.password, self.server, 
                                 self.port, self.search_criteria, self.acquisition_mail_dir, 
                                 self.emails_to_save, self.is_downloading)
        
        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)


        self.worker.finished.connect(self.thread_worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_worker.finished.connect(self.thread_worker.deleteLater)

      
        self.worker.get_emails.connect(self.__handle_get_mails)
        self.worker.download.connect(self.__handle_download)
        
        self.worker.progress.connect(self.__handle_progress)
        self.worker.error.connect(self.__handle_error)

        self.thread_worker.start()

       
    def __handle_error(self, e):

        self.spinner.stop()
        if self.configuration_group_box.isEnabled() is False:
            self.configuration_group_box.setEnabled(True)
        self.setEnabled(True)

        title = mail.SERVER_ERROR
        msg = error.MAIL_SERVER_ERROR
        details = e
        
        if isinstance(e, dict):
            title = e.get('title')
            msg = e.get('msg')
            details = e.get('details')
       
        error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  title,
                                  msg,
                                  str(details))
        error_dlg.exec_()
        

    def __search(self):

        if self.configuration_group_box.isEnabled():
            self.configuration_group_box.setEnabled(False)

        self.spinner.start()
        self.setEnabled(False)

        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()


        #Login params
        self.email = self.input_email.text()
        self.password = self.input_password.text()
        self.server = self.input_server.text()
        self.port = self.input_port.text()

        #Search criteria params
        from_date = self.input_from_date.date() 
        to_date = self.input_to_date.date()
        selected_from_date = from_date.toPyDate()
        selected_to_date = to_date.toPyDate()
        selected_to_date = selected_to_date + timedelta(days=1)

        
        self.search_criteria = self.mail_controller.set_criteria(
        sender=self.input_from.text(),
        recipient=self.input_to.text(),
        subject=self.input_subject.text(),
        from_date=selected_from_date,
        to_date=selected_to_date)

        self.__init_worker()

        self.status.showMessage(Logger.FETCH_EMAILS)
        

    def __start(self):

        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
                'email',
                self.configuration_general.configuration['cases_folder_path'],
                self.case_info['name'],
                self.input_email.text()
            )

        if self.acquisition_directory is not None:
            if self.is_acquisition_running is False:
                self.is_acquisition_running = True
                self.acquisition.start([], self.acquisition_directory, self.case_info, 1)        

    
    def __handle_get_mails(self, emails):

        self.__start()

        self.acquisition.logger.info(Logger.FETCH_EMAILS)
        self.acquisition.logger.info(Logger.SEARCH_CRITERIA.format(self.search_criteria))

        # remove items from tree to clear the acquisition
        if self.folder_tree is not None:
            while self.emails_tree.topLevelItemCount() > 0:
                item = self.emails_tree.takeTopLevelItem(0)
                del item
            self.root = QtWidgets.QTreeWidgetItem([mail.IMAP_FOLDERS])
            self.emails_tree.setHeaderLabel(mail.IMAP_FOUND_EMAILS)
            self.emails_tree.addTopLevelItem(self.root)


        self.setEnabled(True)
        self.status.showMessage('')
        self.spinner.stop()

        if len(emails) == 0:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  mail.NO_EMAILS,
                                  error.NO_EMAILS,
                                  Details.RETRY
                                  )
            error_dlg.exec()

        else:
            self.__add_emails_on_tree_widget(emails)
            self.emails_tree.expandAll()
    
    def __add_emails_on_tree_widget(self, emails):

        for key in emails:
            self.folder_tree = QtWidgets.QTreeWidgetItem([key])
            self.folder_tree.setData(0, Qt.UserRole, key)  # add identifier to the tree items
            self.folder_tree.setCheckState(0, Qt.Unchecked)
            self.root.addChild(self.folder_tree)

            for value in emails[key]:
                sub_item = QtWidgets.QTreeWidgetItem([value])
                sub_item.setData(0, Qt.UserRole, key)
                sub_item.setCheckState(0, Qt.Unchecked)
                self.folder_tree.addChild(sub_item)

        self.emails_tree.expandItem(self.root)
        
        
    def __is_checked(self):
         for i in range(self.root.childCount()):
            parent = self.root.child(i)
            for k in range(parent.childCount()):
                child = parent.child(k)
                if child.checkState(0) == Qt.CheckState.Checked and \
                    self.download_button.isEnabled() is False:
                        self.download_button.setEnabled(True)
            if parent.checkState(0) == Qt.CheckState.Checked and \
                    self.download_button.isEnabled() is False:
                parent.setCheckState(0, False)
        
    def __on_item_changed(self, item, column):
    
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            child.setCheckState(column, item.checkState(column))

        self.download_button.setEnabled(False)
        self.__is_checked()
    
    def __on_editing_finished(self):
         if isinstance(self.sender(), QtWidgets.QLineEdit) and \
            self.sender().objectName() in self.emails_to_validate and \
            self.sender().text() == '' and  self.search_button.isEnabled() is False:
                self.is_valid_email = True
                self.sender().setStyleSheet('')
                self.search_button.setEnabled(True)

    def __on_text_changed(self, text):
        
        if isinstance(self.sender(), QtWidgets.QLineEdit) and \
            self.sender().objectName() in self.emails_to_validate:
            state = self.email_validator.validate(text, 0)
            if state[0] != QRegExpValidator.Acceptable:
                self.is_valid_email = False
                self.sender().setStyleSheet('border: 1px solid red;')
            else:
                self.is_valid_email = True
                self.sender().setStyleSheet('')

        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.search_button.setEnabled(all_fields_filled and self.is_valid_email)

    def __download(self):

        self.emails_to_save = {}
        self.is_downloading = True
        self.setEnabled(False)
        self.__start()
        
        self.status.showMessage(Logger.SAVE_EMAILS)
        self.acquisition.logger.info(Logger.SAVE_EMAILS)

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)

        # wait for 1 second 
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
        
        emails_counter = 0
        for i in range(self.root.childCount()):
            folder = self.root.child(i)
            folder_name = folder.text(0)
            for k in range(folder.childCount()):
                email = folder.child(k)
                if email.checkState(0) == Qt.CheckState.Checked:
                    emails_counter += 1
                    if folder_name in self.emails_to_save:
                        self.emails_to_save[folder_name].append(email.text(0))
                    else:
                        self.emails_to_save[folder_name] = [email.text(0)]
        
       
        # Create acquisition folder
        self.acquisition_mail_dir = os.path.join(self.acquisition_directory, 'acquisition_mail')
        if not os.path.exists(self.acquisition_mail_dir):
            os.makedirs(self.acquisition_mail_dir)

        self.increment = 100/emails_counter
        self.__init_worker()

    
    def __handle_download(self):
            self.is_downloading = False
            self.__zip_and_remove(self.acquisition_mail_dir)
            self.acquisition.set_completed_progress_bar()

            self.acquisition.stop([], '', 1)
            self.acquisition.log_end_message()
        
            self.acquisition.post_acquisition.execute(self.acquisition_directory, self.case_info, 'email')


    def __are_post_acquisition_finished(self):
            self.setEnabled(True)

            self.progress_bar.setHidden(True)
            self.status.showMessage('')

            self.__show_finish_acquisition_dialog()

            self.acquisition_directory = None
            self.is_acquisition_running = False
    
    def __handle_progress(self):
        self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

    def __zip_and_remove(self, mail_dir):

        shutil.make_archive(mail_dir, 'zip', mail_dir)

        try:
            shutil.rmtree(mail_dir)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  tasks.INSTAGRAM,
                                  error.DELETE_PROJECT_FOLDER,
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.exec_()

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.Yes:
            os.startfile(self.acquisition_directory)
        

    def __case(self):
        self.case_view.exec_()

    def __configuration(self):
        self.configuration_view.exec_()

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
