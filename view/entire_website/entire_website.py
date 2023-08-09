# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
import shutil
import logging
import subprocess

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QListWidgetItem, QListWidget, QCheckBox

from view.entire_website.mitm import MitmProxyWorker
from view.menu_bar import MenuBar as MenuBarView

from view.error import Error as ErrorView
from view.spinner import Spinner
from view.acquisition.acquisition import Acquisition

from controller.entire_website import EntireWebsite as EntireWebsiteController

from common.constants import (
    details as Details,
    logger as Logger,
    tasks,
    state,
    status,
    error as Error,
)
from common.constants.view import general, entire_site
from common.utility import get_platform, find_free_port

logger_acquisition = logging.getLogger(__name__)


class EntireWebsiteWorker(QtCore.QObject):
    scraped = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(object)
    valid_url = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(
        self, entire_website_controller, input_url, selected_urls, status, acquisition
    ):
        super().__init__()
        self.entire_website_controller = entire_website_controller
        self.input_url = input_url
        self.url_dir = None
        self.selected_urls = selected_urls
        self.status = status
        self.acquisition = acquisition

    def set_dir(self, dir):
        self.url_dir = dir

    @QtCore.pyqtSlot()
    def run(self):
        if self.entire_website_controller.url is None:
            try:
                self.entire_website_controller.is_valid_url(self.input_url.text())

            except Exception as e:
                self.error.emit(
                    {
                        "title": entire_site.INVALID_URL,
                        "msg": Error.INVALID_URL,
                        "details": e,
                    }
                )
            else:
                self.entire_website_controller.set_url(self.input_url.text())
                self.valid_url.emit()
        else:
            port = find_free_port()
            mitm_thread = MitmProxyWorker(port)
            mitm_thread.set_dir(self.entire_website_controller.acquisition_dir)
            mitm_thread.start()
            self.entire_website_controller.set_proxy(port)
            for url in self.selected_urls:
                try:
                    self.entire_website_controller.download(url)
                    self.status.showMessage(Logger.DOWNLOADED.format(url))
                    self.acquisition.logger.info(Logger.DOWNLOADED.format(url))

                except Exception as e:
                    self.error.emit(
                        {
                            "title": entire_site.INVALID_URL,
                            "msg": Error.INVALID_URL,
                            "details": e,
                        }
                    )
                else:
                    self.progress.emit()
            self.scraped.emit()
        self.finished.emit()


class EntireWebsite(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(EntireWebsite, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.is_enabled_timestamp = False
        self.selected_urls = None
        self.spinner = Spinner()
        self.entire_website_controller = EntireWebsiteController()

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.case_info = case_info

        self.setWindowIcon(QtGui.QIcon(os.path.join("assets/svg/", "FIT.svg")))

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        self.setObjectName("mainWindow")
        self.width = 990
        self.height = 480
        self.setFixedSize(self.width, self.height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setStyleSheet(
            "QWidget {background-color: rgb(255, 255, 255);}"
        )
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        #### - START MENU BAR - #####
        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        # This bar is common on all main window
        self.menu_bar = MenuBarView(self, self.case_info)

        # Add default menu on menu bar
        self.menu_bar.add_default_actions()
        self.setMenuBar(self.menu_bar)
        #### - END MENUBAR - #####

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

        # Get timestamp parameters
        self.configuration_timestamp = (
            self.menu_bar.configuration_view.get_tab_from_name(
                "configuration_timestamp"
            )
        )

        # URL CONFIGURATION GROUP BOX
        self.url_configuration_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.url_configuration_group_box.setEnabled(True)
        self.url_configuration_group_box.setFont(font)
        self.url_configuration_group_box.setGeometry(QtCore.QRect(50, 20, 430, 150))
        self.url_configuration_group_box.setObjectName("configuration_group_box")

        self.label_url = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_url.setGeometry(QtCore.QRect(20, 50, 80, 20))
        self.label_url.setFont(font)
        self.label_url.setObjectName("label_url")

        self.input_url = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_url.setGeometry(QtCore.QRect(50, 50, 350, 20))
        self.input_url.setFont(font)
        self.input_url.setObjectName("input_url")
        self.input_url.setPlaceholderText(entire_site.PLACEHOLDER_URL)

        # LOAD BUTTON
        self.crawl_button = QtWidgets.QPushButton(self)
        self.crawl_button.setGeometry(QtCore.QRect(380, 130, 85, 25))
        self.crawl_button.setObjectName("loadButton")
        self.crawl_button.setFont(font)
        self.crawl_button.clicked.connect(self.__crawl)

        self.crawl_button.setEnabled(False)
        self.input_url.textChanged.connect(
            lambda input: self.__on_text_changed(self.input_url, self.crawl_button)
        )

        # CUSTOM URL GROUP BOX
        self.custom_urls_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.custom_urls_group_box.setFont(font)
        self.custom_urls_group_box.setEnabled(False)
        self.custom_urls_group_box.setGeometry(QtCore.QRect(50, 240, 430, 140))
        self.custom_urls_group_box.setObjectName("custom_urls_group_box")

        self.label_custom_url = QtWidgets.QLabel(self.custom_urls_group_box)
        self.label_custom_url.setGeometry(QtCore.QRect(20, 50, 80, 20))
        self.label_custom_url.setFont(font)
        self.label_custom_url.setObjectName("label_custom_url")

        self.input_custom_url = QtWidgets.QLineEdit(self.custom_urls_group_box)
        self.input_custom_url.setGeometry(QtCore.QRect(50, 50, 330, 20))
        self.input_custom_url.setFont(font)
        self.input_custom_url.setObjectName("input_custom_url")
        self.input_custom_url.setPlaceholderText(entire_site.PLACEHOLDER_CUSTOM_URL)

        # ADD BUTTON
        self.add_button = QtWidgets.QPushButton(self)
        self.add_button.setGeometry(QtCore.QRect(440, 310, 20, 20))
        self.add_button.setStyleSheet(
            "QPushButton { border-radius: 10px; background-color: #4286f4; color: white; font-size: 20px; }"
            "QPushButton:hover { background-color: #1c62cc; }"
        )
        self.add_button.setObjectName("add_button")
        self.add_button.setFont(font)
        self.add_button.clicked.connect(self.__add)
        self.add_button.setEnabled(False)
        self.input_custom_url.textChanged.connect(
            lambda input: self.__on_text_changed(self.input_custom_url, self.add_button)
        )

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)

        # URL PREVIEW GROUP BOX
        self.url_preview_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.url_preview_group_box.setEnabled(True)
        self.url_preview_group_box.setFont(font)
        self.url_preview_group_box.setGeometry(QtCore.QRect(515, 20, 430, 360))
        self.url_preview_group_box.setObjectName("url_preview_group_box")
        self.list_widget = QListWidget(self.url_preview_group_box)
        layout = QtWidgets.QVBoxLayout(self.url_preview_group_box)
        layout.addWidget(self.list_widget)
        self.url_preview_group_box.setLayout(layout)

        # SELECT/DESELECT BUTTON
        self.selector_button = QtWidgets.QPushButton(self)
        self.selector_button.setGeometry(QtCore.QRect(515, 410, 75, 25))
        self.selector_button.setObjectName("selector_button")
        self.selector_button.setFont(font)
        self.selector_button.clicked.connect(self.__select)
        self.selector_button.setEnabled(False)

        # SCRAPE BUTTON
        self.scrape_button = QtWidgets.QPushButton(self)
        self.scrape_button.setGeometry(QtCore.QRect(875, 410, 70, 25))
        self.scrape_button.setObjectName("scrapeButton")
        self.scrape_button.setFont(font)
        self.scrape_button.clicked.connect(self.__scrape)
        self.scrape_button.setEnabled(False)

        self.retranslateUi()

        # ACQUISITION
        self.is_acquisition_running = False
        self.acquisition = Acquisition(
            logger_acquisition, self.progress_bar, self.status, self
        )
        self.acquisition.post_acquisition.finished.connect(
            self.__are_post_acquisition_finished
        )

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.url_configuration_group_box.setTitle(entire_site.URL_CONFIGURATION)
        self.url_preview_group_box.setTitle(entire_site.CRAWLED_URLS)
        self.label_url.setText(entire_site.URL)
        self.scrape_button.setText(general.DOWNLOAD)
        self.custom_urls_group_box.setTitle(entire_site.CUSTOM_URLS)
        self.crawl_button.setText(general.BUTTON_CRAWL)
        self.scrape_button.setText(general.DOWNLOAD)
        self.label_custom_url.setText(entire_site.URL)
        self.add_button.setText(entire_site.ADD)
        self.selector_button.setText(entire_site.DESELECT)

    def __init_worker(self):
        self.thread_worker = QtCore.QThread()
        self.worker = EntireWebsiteWorker(
            self.entire_website_controller,
            self.input_url,
            self.selected_urls,
            self.status,
            self.acquisition,
        )

        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread_worker.quit)

        self.worker.scraped.connect(self.__hanlde_scraped)
        self.worker.progress.connect(self.__handle_progress)
        self.worker.error.connect(self.__handle_error)
        self.worker.valid_url.connect(self.__handle_valid_url)

        self.thread_worker.start()

    def __handle_error(self, e):
        self.spinner.stop()
        if self.url_configuration_group_box.isEnabled() is False:
            self.url_configuration_group_box.setEnabled(True)

        self.setEnabled(True)

        title = entire_site.SERVER_ERROR
        msg = Error.GENERIC_ERROR
        details = e

        if isinstance(e, dict):
            title = e.get("title")
            msg = e.get("msg")
            details = e.get("details")

        error_dlg = ErrorView(
            QtWidgets.QMessageBox.Icon.Information, title, msg, str(details)
        )
        error_dlg.exec()

    def __handle_progress(self):
        self.acquisition.upadate_progress_bar()

    def __crawl(self):
        self.url = self.input_url.text()
        self.entire_website_controller.url = None
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()
        if self.entire_website_controller.url is None:
            self.__init_worker()
            self.custom_urls_group_box.setEnabled(True)
        else:
            self.custom_urls_group_box.setEnabled(True)
            self.__start_scraped()

    def __select(self):
        if self.selector_button.text() == entire_site.DESELECT:
            self.selector_button.setText(entire_site.SELECT)
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                if isinstance(item, QListWidgetItem):
                    widget = self.list_widget.itemWidget(item)
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(False)
        else:
            self.selector_button.setText(entire_site.DESELECT)
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                if isinstance(item, QListWidgetItem):
                    widget = self.list_widget.itemWidget(item)
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(True)

    def __add(self):
        try:
            self.entire_website_controller.is_valid_url(self.input_custom_url.text())
        except Exception as e:
            title = entire_site.INVALID_URL
            msg = Error.INVALID_URL
            details = e
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Information, title, msg, str(details)
            )
            error_dlg.exec()
        else:
            if not self.__item_exists_in_list_widget(
                self.list_widget, self.input_custom_url.text()
            ):
                item = QListWidgetItem()
                check_box = QCheckBox(self.input_custom_url.text())
                item.setSizeHint(check_box.sizeHint())
                check_box.setChecked(True)
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, check_box)

    def __item_exists_in_list_widget(self, list_widget, text):
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if isinstance(item, QListWidgetItem):
                widget = list_widget.itemWidget(item)
                if isinstance(widget, QCheckBox):
                    if widget.text() == text:
                        return True
        return False

    def __scrape(self):
        self.url = self.input_url.text()
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()
        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()
        if self.entire_website_controller.url is None:
            self.__init_worker()
        else:
            self.__start_scraped()

    def __handle_valid_url(self):
        self.thread_worker.quit()
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()

        self.__crawl_url()

    def __crawl_url(self):
        self.setEnabled(True)
        self.status.showMessage("")

        urls = self.entire_website_controller.check_sitemap()
        self.list_widget.clear()
        for url in urls:
            item = QListWidgetItem()
            check_box = QCheckBox(url)
            item.setSizeHint(check_box.sizeHint())
            check_box.setChecked(True)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, check_box)
        self.scrape_button.setEnabled(True)
        self.selector_button.setEnabled(True)
        self.spinner.stop()
        self.is_acquisition_running = False

    def __start_scraped(self):
        if self.acquisition_directory is None:
            self.acquisition_directory = (
                self.menu_bar.case_view.form.controller.create_acquisition_directory(
                    "entire_website",
                    self.configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                    self.input_url.text(),
                )
            )

        self.is_acquisition_running = True

        self.selected_urls = []
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            check_box = self.list_widget.itemWidget(item)
            if check_box.isChecked():
                self.selected_urls.append(check_box.text())

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.acquisition.start(
            [], self.acquisition_directory, self.case_info, len(self.selected_urls)
        )

        self.status.showMessage(Logger.DOWNLOAD_WEBSITE)
        self.acquisition.logger.info(Logger.DOWNLOAD_WEBSITE)
        self.acquisition.info.add_task(
            tasks.DOWNLOAD_WEBSITE, state.STARTED, status.PENDING
        )

        self.entire_website_controller.set_dir(self.acquisition_directory)
        # external tasks
        external_tasks = [tasks.PACKET_CAPTURE]
        self.acquisition.start(
            external_tasks, self.acquisition_directory, self.case_info
        )
        self.__init_worker()

    def __hanlde_scraped(self):
        row = self.acquisition.info.get_row(tasks.DOWNLOAD_WEBSITE)
        self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, "")

        self.__zip_and_remove(
            os.path.join(self.acquisition_directory, "acquisition_page")
        )
        # external tasks
        external_tasks = [
            tasks.PACKET_CAPTURE,
            tasks.WHOIS,
            tasks.NSLOOKUP,
            tasks.HEADERS,
            tasks.TRACEROUTE,
            tasks.SSLKEYLOG,
            tasks.SSLCERTIFICATE,
            tasks.SCREEN_RECORDER,
        ]

        self.acquisition.stop(external_tasks, self.url, len(external_tasks))
        self.acquisition.log_end_message()
        self.spinner.stop()

        self.acquisition.post_acquisition.execute(
            self.acquisition_directory, self.case_info, "entire_website"
        )

    def __are_post_acquisition_finished(self):
        self.acquisition.set_completed_progress_bar()

        self.progress_bar.setHidden(True)
        self.status.showMessage("")
        self.setEnabled(True)

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_acquisition_running = False

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
        )

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__open_acquisition_directory()

    def __zip_and_remove(self, directory):
        shutil.make_archive(directory, "zip", directory)

        try:
            shutil.rmtree(directory)
        except OSError as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                tasks.DOWNLOAD_WEBSITE,
                Error.DELETE_PROJECT_FOLDER,
                "Error: %s - %s." % (e.filename, e.strerror),
            )

            error_dlg.exec()

    def __open_acquisition_directory(self):
        platform = get_platform()

        if platform == "win":
            os.startfile(self.acquisition_directory)
        elif platform == "osx":
            subprocess.call(["open", self.acquisition_directory])
        else:  # platform == 'lin' || platform == 'other'
            subprocess.call(["xdg-open", self.acquisition_directory])

    def __on_text_changed(self, input, button):
        all_field_filled = bool(input.text())
        button.setEnabled(all_field_filled)

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
