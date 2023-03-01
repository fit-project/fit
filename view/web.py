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

import logging.config
import shutil
from mitmproxy import ctx
from scapy.all import *
import ssl
import asyncio
import certifi

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtNetwork import QSslCertificate, QSslConfiguration, QNetworkProxy
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile

from view.screenrecorder import ScreenRecorder as ScreenRecorderView
from view.packetcapture import PacketCapture as PacketCaptureView
from view.acquisitionstatus import AcquisitionStatus as AcquisitionStatusView
from view.timestamp import Timestamp as TimestampView
from view.proxyserver import ProxyServer as ProxyServerView
from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView

from controller.report import Report as ReportController
from controller.warc_creator import WarcCreator as WarcCreatorController

from common.error import ErrorMessage

from common.settings import DEBUG
from common.config import LogConfig
import common.utility as utility

import sslkeylog


logger_acquisition = logging.getLogger(__name__)
logger_hashreport = logging.getLogger('hashreport')
logger_whois = logging.getLogger('whois')
logger_headers = logging.getLogger('headers')
logger_nslookup = logging.getLogger('nslookup')


class MitmThread(QThread):
    def __init__(self, port, acquisition_directory):
        super().__init__()
        self.port = port
        self.acquisition_directory = acquisition_directory

    def run(self):
        # create new event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # mitmproxy's creation
        self.proxy_server = ProxyServerView(self.port, self.acquisition_directory)
        asyncio.run(self.proxy_server.start())

    def stop_proxy(self):
        try:
            ctx.master.shutdown()
            ctx.master = None
        except: pass

class MainWindow(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        der_data = self.set_ssl_config()
        pem_data = ssl.DER_cert_to_PEM_cert(der_data)

        self.page().profile().setHttpUserAgent(pem_data)

    # ssl configurations (not working for me, I had to install the certificate on my machine)
    def set_ssl_config(self):
        # get the pem with openssl from the mitmproxy .p12
        # openssl pkcs12 -in {mitmproxy-ca-cert.p12} -out {cert_pem} -nodes

        # add pem to the trusted root certificates (won't solve the problem)
        cert_file_path = certifi.where()
        pem_path = 'asset/cert/mitmproxy-ca-cert.pem'
        with open(pem_path, 'rb') as pem_file:
            pem_data = pem_file.read()
        with open(cert_file_path, 'ab') as cert_file:
            cert_file.write(pem_data)

        # create a QSslConfiguration object with the certificate as the CA certificate (won't solve the problem neither)
        cert = QSslCertificate(pem_data)
        config = QSslConfiguration.defaultConfiguration()
        config.setCaCertificates([cert])

        # get the DER-encoded certificate data
        der_data = cert.toDer()
        return der_data

    def closeEvent(self, event):
        self.page().profile().clearHttpCache()


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
        QtCore.QTimer.singleShot(500, self.take_screenshot)

    def take_screenshot(self):
        self.grab().save(self.output_file, b'PNG')
        self.close()


class Web(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()  # make a stop signal to communicate with the workers in another threads

    def __init__(self, *args, **kwargs):
        if not os.path.isdir("resources"):
            os.makedirs("resources")
        super(Web, self).__init__(*args, **kwargs)
        self.error_msg = ErrorMessage()
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.acquisition_status = AcquisitionStatusView(self)
        self.acquisition_status.setupUi()
        self.log_confing = LogConfig()
        self.is_enabled_screen_recorder = False
        self.is_enabled_packet_capture = False
        self.is_enabled_timestamp = False

    def init(self, case_info):

        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()

        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

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

        back_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'arrow-180.png')), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.back())
        navtb.addAction(back_btn)

        next_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'arrow-000.png')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.forward())
        navtb.addAction(next_btn)

        self.reload_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'arrow-circle-315.png')), "Reload",
                                            self)
        self.reload_btn.setStatusTip("Reload page")
        self.reload_btn.triggered.connect(lambda: self.reload())
        navtb.addAction(self.reload_btn)

        home_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.httpsicon = QtWidgets.QLabel()  # Yes, really!
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('asset/images', 'lock-nossl.png')))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QtWidgets.QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'cross-circle.png')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        tab_menu = self.menuBar().addMenu("&Tab")
        new_tab_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'ui-tab--plus.png')), "New Tab",
                                           self)
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        tab_menu.addAction(new_tab_action)

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
        start_acquisition_action.triggered.connect(self.start_acquisition)
        acquisition_menu.addAction(start_acquisition_action)
        stop_acquisition_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'stop.png')), "Stop", self)
        stop_acquisition_action.setObjectName('StopAcquisitionAction')
        stop_acquisition_action.triggered.connect(self.stop_acquisition)
        acquisition_menu.addAction(stop_acquisition_action)
        acquisition_status_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'info.png')), "Status",
                                                      self)
        acquisition_status_action.setObjectName('StatusAcquisitionAction')
        acquisition_status_action.triggered.connect(self._acquisition_status)
        acquisition_menu.addAction(acquisition_status_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        # Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')

        # Get timestamp parameters
        self.configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")

        self.add_new_tab(QtCore.QUrl(self.configuration_general.configuration['home_page_url']), 'Homepage')

        self.show()

        self.setWindowTitle("Freezing Internet Tool")
        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

        # Enable/Disable other modules logger
        if not DEBUG:
            loggers = [logging.getLogger()]  # get the root logger
            loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict if
                                 name not in [__name__, 'hashreport']]

            self.log_confing.disable_loggers(loggers)

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

        # set port and start the thread
        port = 8081
        self.mitm_thread = MitmThread(port, self.acquisition_directory)

        # create the proxy
        self.proxy = QNetworkProxy(QNetworkProxy.HttpProxy, '127.0.0.1', 8081)
        QNetworkProxy.setApplicationProxy(self.proxy)

        # start mitm_thread
        self.mitm_thread.start()
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

            # refreshing the page so we can get back the resources already loaded
            # tricky way to refresh the url

            self.tabs.currentWidget().page().profile().clearHttpCache()
            cookie_store = self.tabs.currentWidget().page().profile().cookieStore()
            # Delete all cookies from the store
            cookie_store.deleteAllCookies()
            self.tabs.currentWidget().page().profile().clearAllVisitedLinks()
            self.reload_btn.trigger()

            # Step 4: Add new thread for network packet capture and start it
            self.configuration_packetcapture = self.configuration_view.get_tab_from_name("configuration_packetcapture")
            options = self.configuration_packetcapture.options
            self.is_enabled_packet_capture = options['enabled']
            if self.is_enabled_packet_capture:
                options['acquisition_directory'] = self.acquisition_directory
                self.start_packet_capture(options)
                self.acquisition_status.add_task('Network Packet Capture')
                self.acquisition_status.set_status('Network Packet Capture',
                                                   'Capture loop has been started in a new thread!', 'done')
                logger_acquisition.info('Network Packet Capture started')
                self.status.showMessage('Capture loop has been started in a new thread!')
                self.progress_bar.setValue(75)

            # Step 5: Add new thread for screen video recoder and start it
            self.configuration_screenrecorder = self.configuration_view.get_tab_from_name(
                "configuration_screenrecorder")
            options = self.configuration_screenrecorder.options
            self.is_enabled_screen_recorder = bool(options['enabled'])

            if self.is_enabled_screen_recorder:
                options['filename'] = os.path.join(self.acquisition_directory, options['filename'])
                self.start_screen_recoder(options)
                self.acquisition_status.add_task('Screen Recoder')
                self.acquisition_status.set_status('Screen Recoder', 'Recoder loop has been started in a new thread!',
                                                   'done')
                self.status.showMessage('Recoder loop has been started in a new thread!')
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
            url = self.tabs.currentWidget().url().toString()

            # Step 1: Disable all actions and clear current acquisition information on dialog
            self.setEnabled(False)
            self.acquisition_status.clear()
            self.acquisition_status.set_title('Interruption of the acquisition in progress:')
            logger_acquisition.info('Acquisition stopped')
            logger_acquisition.info('End URL: ' + url)
            self.statusBar().showMessage('Message in statusbar.')

            ### START NETWORK CHECK ###
            # Step 2: Get whois info
            logger_acquisition.info('Get WHOIS info for URL: ' + url)
            logger_whois.info(utility.whois(url))
            self.status.showMessage('Get WHOIS info')
            self.progress_bar.setValue(1)

            # Step 3: Get nslookup info
            logger_acquisition.info('Get NSLOOKUP info for URL: ' + url)
            logger_nslookup.info(utility.nslookup(url,
                                                  self.configuration_network.configuration["nslookup_dns_server"],
                                                  self.configuration_network.configuration["nslookup_enable_tcp"],
                                                  self.configuration_network.configuration[
                                                      "nslookup_enable_verbose_mode"]
                                                  ))

            self.status.showMessage('Get WHOIS info')
            self.progress_bar.setValue(2)

            # Step 4: Get headers info
            logger_acquisition.info('Get HEADERS info for URL: ' + url)
            logger_headers.info(utility.get_headers_information(url))

            self.status.showMessage('Get HEADERS info')
            self.progress_bar.setValue(3)

            # Step 5: Get traceroute info
            logger_acquisition.info('Get TRACEROUTE info for URL: ' + url)
            utility.traceroute(url, os.path.join(self.acquisition_directory, 'traceroute.txt'))
            self.status.showMessage('Get TRACEROUTE info')
            self.progress_bar.setValue(8)
            ### END NETWORK CHECK ###

            ### START GET SSLKEYLOG AND SSL CERTIFICATE ###
            # Step 6: Get sslkey.log
            logger_acquisition.info('Get SSLKEYLOG')
            sslkeylog.set_keylog(os.path.join(self.acquisition_directory, 'sslkey.log'))
            self.status.showMessage('Get SSLKEYLOG')
            self.progress_bar.setValue(9)

            # Step 7: Get peer SSL certificate
            if utility.check_if_peer_certificate_exist(url):
                logger_acquisition.info('Get SSL certificate for URL:' + url)
                certificate = utility.get_peer_PEM_cert(url)
                utility.save_PEM_cert_to_CER_cert(os.path.join(self.acquisition_directory, 'server.cer'), certificate)
                self.status.showMessage('Get SSL CERTIFICATE')
                self.progress_bar.setValue(10)
            ### END GET SSLKEYLOG AND SSL CERTIFICATE ###

            # Step 6: stop threads
            if self.is_enabled_packet_capture:
                self.packetcapture.stop()

            if self.is_enabled_screen_recorder:
                self.screenrecorder.stop()

            # Step 7:  Save screenshot of current page
            self.status.showMessage('Save screenshot of current page')
            self.progress_bar.setValue(10)
            logger_acquisition.info('Save screenshot of current page')
            screenshot = Screenshot()
            screenshot.capture(url,
                               os.path.join(self.acquisition_directory, 'screenshot.png'))

            self.acquisition_status.add_task('Screenshot Page')
            self.acquisition_status.set_status('ScreenShot Page', 'Screenshot of current web page is done!', 'done')

            self.status.showMessage('Save all resource of current page')
            self.progress_bar.setValue(20)

            # Step 8:  Save all resource of current page

            self.mitm_thread.stop_proxy()

            self.proxy.setType(QNetworkProxy.DefaultProxy)
            QNetworkProxy.setApplicationProxy(self.proxy)
            # set the proxy for the manager to the NoProxy object
            self.tabs.currentWidget().page().profile().clearHttpCache()
            cookie_store = self.tabs.currentWidget().page().profile().cookieStore()
            # Delete all cookies from the store
            cookie_store.deleteAllCookies()
            self.tabs.currentWidget().page().profile().clearAllVisitedLinks()

            # create wacz when acquisition is finished
            warc_path = f'{self.acquisition_directory}/acquisition_warc.warc'
            wacz_path = f'{self.acquisition_directory}/acquisition_wacz.wacz'
            pages_path = f'{self.acquisition_directory}/acquisition_pages.jsonl'

            warc_creator = WarcCreatorController()
            if os.path.exists(warc_path):
                warc_creator.create_pages(pages_path, warc_path)
                warc_creator.warc_to_wacz(pages_path, warc_path, wacz_path)

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
            # Step 9:  Calculate acquisition hash
            logger_acquisition.info('Calculate acquisition file hash')
            files = [f.name for f in os.scandir(self.acquisition_directory) if f.is_file()]

            for file in files:
                if file != 'acquisition.hash':
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

            ntp = utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])
            logger_acquisition.info(f'NTP end acquisition time: {ntp}')

            logger_acquisition.info('Acquisition end')

            logger_acquisition.info('PDF generation start')
            ### generate pdf report ###
            report = ReportController(self.acquisition_directory, self.case_info)
            report.generate_pdf('web', ntp)
            logger_acquisition.info('PDF generation end')

            ### generate timestamp for the report ###
            options = self.configuration_timestamp.options
            self.is_enabled_timestamp = options['enabled']
            if self.is_enabled_timestamp:
                self.timestamp = TimestampView()
                self.timestamp.set_options(options)
                self.timestamp.apply_timestamp(self.acquisition_directory, 'acquisition_report.pdf')

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
                                           'Loop has been stopped and .pcap file has been saved in the case folder',
                                           'done')
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
                                           'Loop has been stopped and .avi file has been saved in the case folder',
                                           'done')
        self.th_screenrecorder.quit()
        self.th_screenrecorder.wait()

    def save_page(self):
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

        browser = MainWindow()
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
