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

from controller.mail import Mail as MailController


# TODO: Implement this view as a two input window (email an password),
#  then call the proper method inside the controller to start the acquisition

# this view is defined as a foo method, just for testing.
# you can test it with mail = MailView() inside fit.py's main
# I kept the button disabled but changed the color of the frame and the image in the wizard
# still under development


import os
import logging
import logging.config
import shutil

from pywebcopy import save_webpage

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from view.acquisitionstatus import AcquisitionStatus as AcquisitionStatusView

from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView

from common.error import ErrorMessage

from common.settings import DEBUG
from common.config import LogConfig
import common.utility as utility

logger_acquisition = logging.getLogger(__name__)
logger_hashreport = logging.getLogger('hashreport')


class Screenshot(QtWebEngineWidgets.QWebEngineView):

    def capture(self, url, output_file):
        self.output_file = output_file
        self.load(QtCore.QUrl(url))
        self.loadFinished.connect(self.on_loaded)
        # Create hidden view without scrollbars
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen)
        self.page().settings().setAttribute(
            QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
        self.show()

    def on_loaded(self):
        size = self.page().contentsSize().toSize()
        self.resize(size)
        # Wait for resize
        QtCore.QTimer.singleShot(1000, self.take_screenshot)

    def take_screenshot(self):
        self.grab().save(self.output_file, b'PNG')
        self.close()

# TODO: change interface, check for logger not writing in file
class Mail(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()  # make a stop signal to communicate with the workers in another threads

    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        self.input_email = None
        self.input_password = None
        self.error_msg = ErrorMessage()
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.acquisition_status = AcquisitionStatusView(self)
        self.acquisition_status.setupUi()
        self.log_confing = LogConfig()

    def init(self, case_info):

        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()

        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.progress_bar.setFixedHeight(25)
        self.status.addPermanentWidget(self.progress_bar)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.setStatusBar(self.status)
        self.progress_bar.setHidden(True)

        navtb = QtWidgets.QToolBar("Navigation")
        navtb.setObjectName('NavigationToolBar')
        navtb.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(navtb)

        navtb.addSeparator()

        self.input_email = QtWidgets.QLineEdit()
        navtb.addWidget(self.input_email)
        self.input_password = QtWidgets.QLineEdit()
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.show()
        navtb.addWidget(self.input_password)

        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        tab_menu = self.menuBar().addMenu("&Tab")
        new_tab_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'ui-tab--plus.png')), "New Tab",
                                           self)

        # CONFIGURATION ACTION
        configuration_action = QtWidgets.QAction("Configuration", self)
        configuration_action.setStatusTip("Show configuration info")
        configuration_action.triggered.connect(self.configuration)
        self.menuBar().addAction(configuration_action)

        # CASE ACTION
        case_action = QtWidgets.QAction("Case", self)
        case_action.setStatusTip("Show case info")
        case_action.triggered.connect(self.case)
        self.menuBar().addAction(case_action)

        # ACQUISITION MENU
        acquisition_menu = self.menuBar().addMenu("&Acquisition")

        start_acquisition_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'start.png')), "Start",
                                                     self)
        start_acquisition_action.setObjectName('StartAcquisitionAction')
        start_acquisition_action.triggered.connect(self.start_dump_email)
        acquisition_menu.addAction(start_acquisition_action)

        acquisition_status_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'info.png')), "Status",
                                                      self)
        acquisition_status_action.setObjectName('StatusAcquisitionAction')
        acquisition_status_action.triggered.connect(self._acquisition_status)
        acquisition_menu.addAction(acquisition_status_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")


        self.show()

        self.setWindowTitle("Freezing Internet Tool")
        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

        # Enable/Disable other modules logger
        if not DEBUG:
            loggers = [logging.getLogger()]  # get the root logger
            loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict if
                                 name not in [__name__, 'hashreport']]

            self.log_confing.disable_loggers(loggers)

    def start_dump_email(self):

        # Step 1: Disable start_acquisition_action and clear current threads and acquisition information on dialog
        action = self.findChild(QtWidgets.QAction, 'StartAcquisitionAction')
        self.progress_bar.setValue(50)
        if action is not None:
            action.setEnabled(False)

        self.acquisition_status.clear()
        self.acquisition_status.set_title('Acquisition is started!')

        # Step 2: Create acquisiton directory
        self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
            'mail',
            self.configuration_general.configuration['cases_folder_path'],
            self.case_info['name'],
            self.input_email.text()
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
            self.acquisition_status.add_task('Logger')
            self.acquisition_status.set_status('Logger', 'Started', 'done')
            self.status.showMessage('Logging handler and login information have been started')
            self.progress_bar.setValue(100)

            self.acquisition_status.set_title('Acquisition started success:')

            # hidden progress bar
            self.progress_bar.setHidden(True)
            self.status.showMessage('')
            if self.acquisition_is_started:
                self.progress_bar.setHidden(False)

                # Step 1: Disable all actions and clear current acquisition information on dialog
                self.setEnabled(False)
                self.acquisition_status.clear()
                self.acquisition_status.set_title('Interruption of the acquisition in progress:')
                logger_acquisition.info('Acquisition stopped')
                logger_acquisition.info('Emil scraping')  # change this
                self.statusBar().showMessage('Message in statusbar.')

                self.status.showMessage('Save all resource of current page')
                self.progress_bar.setValue(20)
                # Step 4:  Save all resource of current page
                zip_folder = self.save_messages()

                logger_acquisition.info('Save all resource of current page')
                self.acquisition_status.add_task('Save Page')
                self.acquisition_status.set_status('Save Page', zip_folder, 'done')

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


    def save_messages(self):

        email = self.input_email.text()
        password = self.input_password.text()
        project_folder = self.acquisition_directory
        mail_controller = MailController(email, password, project_folder)
        mail_controller.get_mails_from_every_folder()

        project_name = "emails"

        acquisition_page_folder = os.path.join(project_folder, project_name)
        zip_folder = shutil.make_archive(acquisition_page_folder, 'zip', acquisition_page_folder)
        try:
            shutil.rmtree(acquisition_page_folder)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['save_mail'],
                                  self.error_msg.MESSAGES['save_mail'],
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.buttonClicked.connect(quit)
            error_dlg.exec_()

        return zip_folder

    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

