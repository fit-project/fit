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

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from view.screenrecorder import ScreenRecorder as ScreenRecorderView
from view.packetcapture import PacketCapture as PacketCaptureView
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


class Mail(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

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
        self.setObjectName("mainWindow")
        self.resize(500, 266)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(330, 200, 118, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar"
                                       )
        self.input_email = QtWidgets.QLineEdit(self.centralwidget)
        self.input_email.setGeometry(QtCore.QRect(210, 50, 240, 20))
        self.input_email.setObjectName("input_email")

        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(210, 100, 240, 20))
        self.input_password.setObjectName("input_password")

        self.label_email = QtWidgets.QLabel(self.centralwidget)
        self.label_email.setGeometry(QtCore.QRect(50, 50, 100, 20))
        self.label_email.setObjectName("label_email")

        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(50, 100, 100, 20))
        self.label_password.setObjectName("label_password")

        self.scrapeButton = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton.setGeometry(QtCore.QRect(370, 150, 75, 25))
        self.scrapeButton.setObjectName("scrapeButton")

        self.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 500, 21))
        self.menuBar.setObjectName("menuBar")

        self.menuConfiguration = QtWidgets.QMenu(self.menuBar)
        self.menuConfiguration.setObjectName("menuConfiguration")
        self.menuCase = QtWidgets.QMenu(self.menuBar)
        self.menuCase.setObjectName("menuCase")




        self.menuAcquisition = QtWidgets.QMenu(self.menuBar)
        self.menuAcquisition.setObjectName("menuAcquisition")

        self.setMenuBar(self.menuBar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.actionAcquisition_Info = QtWidgets.QAction(self)
        self.actionAcquisition_Info.setObjectName("actionAcquisition_Info")

        self.menuAcquisition.addAction(self.actionAcquisition_Info)

        self.menuBar.addAction(self.menuConfiguration.menuAction())
        self.menuBar.addAction(self.menuCase.menuAction())
        self.menuBar.addAction(self.menuAcquisition.menuAction())

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "Freezing Internet Tool"))
        self.label_email.setText(_translate("mainWindow", "Inserisci l\'email"))
        self.label_password.setText(_translate("mainWindow", "Inserisci la password"))
        self.scrapeButton.setText(_translate("mainWindow", "Scrape"))
        self.menuConfiguration.setTitle(_translate("mainWindow", "Configuration"))
        self.menuCase.setTitle(_translate("mainWindow", "Case"))
        self.menuAcquisition.setTitle(_translate("mainWindow", "Acquisition"))
        self.actionAcquisition_Info.setText(_translate("mainWindow", "Status"))


def start_acquisition(self):
    # Step 1: Disable start_acquisition_action and clear current threads and acquisition information on dialog
    action = self.findChild(QtWidgets.QAction, 'StartAcquisitionAction')
    self.progress_bar.setValue(50)
    if action is not None:
        action.setEnabled(False)

    self.acquisition_status.clear()
    self.acquisition_status.set_title('Acquisition is started!')

    # Step 2: Create acquisiton directory
    self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
        'web',
        self.configuration_general.configuration['cases_folder_path'],
        self.case_info['name'],
        self.tabs.currentWidget().url().toString()
    )
    if self.acquisition_directory is not None:

        print('qui sono in start')
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
        self.progress_bar.setValue(50)

        # Step 4: Add new thread for network packet capture and start it
        self.configuration_packetcapture = self.configuration_view.get_tab_from_name("configuration_packetcapture")
        options = self.configuration_packetcapture.options
        self.is_enabled_packet_capture = options['enabled']
        if self.is_enabled_packet_capture:
            options['acquisition_directory'] = self.acquisition_directory
            self.start_packet_capture(options)
            self.acquisition_status.add_task('Network Packet Capture')
            self.acquisition_status.set_status('Network Packet Capture',
                                               'Capture loop has been starded in a new thread!', 'done')
            logger_acquisition.info('Network Packet Capture started')
            self.status.showMessage('Capture loop has been starded in a new thread!')
            self.progress_bar.setValue(75)

        # Step 5: Add new thread for screen video recoder and start it
        self.configuration_screenrecorder = self.configuration_view.get_tab_from_name("configuration_screenrecorder")
        options = self.configuration_screenrecorder.options
        self.is_enabled_screen_recorder = bool(options['enabled'])

        if self.is_enabled_screen_recorder:
            options['filename'] = os.path.join(self.acquisition_directory, options['filename'])
            self.start_screen_recoder(options)
            self.acquisition_status.add_task('Screen Recoder')
            self.acquisition_status.set_status('Screen Recoder', 'Recoder loop has been starded in a new thread!',
                                               'done')
            self.status.showMessage('Recoder loop has been starded in a new thread!')
            self.progress_bar.setValue(100)
            logger_acquisition.info('Screen recoder started')
            logger_acquisition.info('Initial URL: ' + self.tabs.currentWidget().url().toString())
            self.acquisition_status.set_title('Acquisition started success:')

        # hidden progress bar
        self.progress_bar.setHidden(True)
        self.status.showMessage('')


def stop_acquisition(self):
    if self.acquisition_is_started:
        self.progress_bar.setHidden(False)

        # Step 1: Disable all actions and clear current acquisition information on dialog
        self.setEnabled(False)
        self.acquisition_status.clear()
        self.acquisition_status.set_title('Interruption of the acquisition in progress:')
        logger_acquisition.info('Acquisition stopped')
        logger_acquisition.info('End URL: ' + self.tabs.currentWidget().url().toString())
        self.statusBar().showMessage('Message in statusbar.')
        # Step 2: stop threads
        if self.is_enabled_packet_capture:
            self.packetcapture.stop()

        if self.is_enabled_screen_recorder:
            self.screenrecorder.stop()

        # Step 3:  Save screenshot of current page
        self.status.showMessage('Save screenshot of current page')
        self.progress_bar.setValue(10)
        logger_acquisition.info('Save screenshot of current page')
        screenshot = Screenshot()
        screenshot.capture(self.tabs.currentWidget().url().toString(),
                           os.path.join(self.acquisition_directory, 'screenshot.png'))

        self.acquisition_status.add_task('Screenshot Page')
        self.acquisition_status.set_status('ScreenShot Page', 'Screenshot of current web page is done!', 'done')

        self.status.showMessage('Save all resource of current page')
        self.progress_bar.setValue(20)
        # Step 4:  Save all resource of current page
        zip_folder = self.save_page()

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


def start_packet_capture(self, options):
    self.th_packetcapture = QtCore.QThread()

    self.packetcapture = PacketCaptureView()
    self.packetcapture.set_options(options)

    self.packetcapture.moveToThread(self.th_packetcapture)

    self.th_packetcapture.started.connect(self.packetcapture.start)
    self.packetcapture.finished.connect(self.th_packetcapture.quit)
    self.packetcapture.finished.connect(self.packetcapture.deleteLater)
    self.th_packetcapture.finished.connect(self.th_packetcapture.deleteLater)
    self.th_packetcapture.finished.connect(self._thread_packetcapture_is_finished)

    self.th_packetcapture.start()


def _thread_packetcapture_is_finished(self):
    self.status.showMessage('Loop has been stopped and .pcap file has been saved in the case folder')
    value = self.progress_bar.value() + 30
    self.progress_bar.setValue(value)
    logger_acquisition.info('Network Packet Capture stopped')
    self.acquisition_status.add_task('Network Packet Capture')
    self.acquisition_status.set_status('Network Packet Capture',
                                       'Loop has been stopped and .pcap file has been saved in the case folder', 'done')
    self.th_packetcapture.quit()
    self.th_packetcapture.wait()


def start_screen_recoder(self, options):
    self.th_screenrecorder = QtCore.QThread()

    self.screenrecorder = ScreenRecorderView()
    self.screenrecorder.set_options(options)

    self.screenrecorder.moveToThread(self.th_screenrecorder)

    self.th_screenrecorder.started.connect(self.screenrecorder.start)
    self.screenrecorder.finished.connect(self.th_screenrecorder.quit)
    self.screenrecorder.finished.connect(self.screenrecorder.deleteLater)
    self.th_screenrecorder.finished.connect(self.th_screenrecorder.deleteLater)
    self.th_screenrecorder.finished.connect(self._thread_screenrecorder_is_finished)

    self.th_screenrecorder.start()


def _thread_screenrecorder_is_finished(self):
    self.status.showMessage('Loop has been stopped and .avi file has been saved in the case folder')
    value = self.progress_bar.value() + 30
    self.progress_bar.setValue(value)
    logger_acquisition.info('Screen recoder stopped')
    self.acquisition_status.add_task('Screen Recoder')
    self.acquisition_status.set_status('Screen Recoder',
                                       'Loop has been stopped and .avi file has been saved in the case folder', 'done')
    self.th_screenrecorder.quit()
    self.th_screenrecorder.wait()


def save_page(self):
    url = self.tabs.currentWidget().url().toString()

    project_folder = self.acquisition_directory

    project_name = "acquisition_page"


    acquisition_page_folder = os.path.join(project_folder, project_name)
    zip_folder = shutil.make_archive(acquisition_page_folder, 'zip', acquisition_page_folder)
    try:
        shutil.rmtree(acquisition_page_folder)
    except OSError as e:
        error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                              self.error_msg.TITLES['save_web_page'],
                              self.error_msg.MESSAGES['delete_project_folder'],
                              "Error: %s - %s." % (e.filename, e.strerror)
                              )

        error_dlg.buttonClicked.connect(quit)
        error_dlg.exec_()

    return zip_folder


def case(self):
    self.case_view.exec_()


def configuration(self):
    self.configuration_view.exec_()


def back(self):
    if self.acquisition_is_started:
        logger_acquisition.info('User clicked the back button')
    self.tabs.currentWidget().back()


def forward(self):
    if self.acquisition_is_started:
        logger_acquisition.info('User clicked the forward button')
    self.tabs.currentWidget().forward()


def reload(self):
    if self.acquisition_is_started:
        logger_acquisition.info('User clicked the reload button')
    self.tabs.currentWidget().reload()


def add_new_tab(self, qurl=None, label="Blank"):
    if self.acquisition_is_started:
        logger_acquisition.info('User add new tab')

    if qurl is None:
        qurl = QtCore.QUrl('')

    browser = QtWebEngineWidgets.QWebEngineView()
    browser.setUrl(qurl)
    i = self.tabs.addTab(browser, label)

    self.tabs.setCurrentIndex(i)

    # More difficult! We only want to update the url when it's from the
    # correct tab
    browser.urlChanged.connect(lambda qurl, browser=browser:
                               self.update_urlbar(qurl, browser))

    browser.loadProgress.connect(self.load_progress)

    browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                 self.tabs.setTabText(i, browser.page().title()))

    if i == 0:
        self.showMaximized()


def tab_open_doubleclick(self, i):
    if i == -1:  # No tab under the click
        self.add_new_tab()


def current_tab_changed(self, i):
    qurl = self.tabs.currentWidget().url()
    self.update_urlbar(qurl, self.tabs.currentWidget())
    self.update_title(self.tabs.currentWidget())


def close_current_tab(self, i):
    if self.acquisition_is_started:
        logger_acquisition.info('User remove tab')
    if self.tabs.count() < 2:
        return

    self.tabs.removeTab(i)


def update_title(self, browser):
    if browser != self.tabs.currentWidget():
        # If this signal is not from the current tab, ignore
        return

    title = self.tabs.currentWidget().page().title()
    self.setWindowTitle("%s - Freezing Internet Tool" % title)


def navigate_home(self):
    if self.acquisition_is_started:
        logger_acquisition.info('User clicked the home button')

    self.tabs.currentWidget().setUrl(QtCore.QUrl(self.configuration_general.configuration['home_page_url']))


def navigate_to_url(self):  # Does not receive the Url
    q = QtCore.QUrl(self.urlbar.text())
    if q.scheme() == "":
        q.setScheme("http")

    self.tabs.currentWidget().setUrl(q)


def load_progress(self, prog):
    if self.acquisition_is_started and prog == 100:
        logger_acquisition.info('Loaded: ' + self.tabs.currentWidget().url().toString())


def update_urlbar(self, q, browser=None):
    if browser != self.tabs.currentWidget():
        # If this signal is not from the current tab, ignore
        return

    if q.scheme() == 'https':
        # Secure padlock icon
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('asset/images', 'lock-ssl.png')))

    else:
        # Insecure padlock icon
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('asset/images', 'lock-nossl.png')))

    self.urlbar.setText(q.toString())
    self.urlbar.setCursorPosition(0)


def closeEvent(self, event):
    packetcapture = getattr(self, 'packetcapture', None)

    if packetcapture is not None:
        packetcapture.stop()
