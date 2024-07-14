#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging
import os.path

from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from view.scrapers.web.web_engine_view import WebEngineView, WebEnginePage
from view.util import (
    show_configuration_dialog,
    show_case_info_dialog,
    show_finish_acquisition_dialog,
    show_acquisition_info_dialog,
    screenshot_filename,
)

from view.scrapers.web.selected_area_screenshot import SelectAreaScreenshot
from view.scrapers.web.full_page_screenshot import FullPageScreenShot
from view.scrapers.web.acquisition import WebAcquisition, AcquisitionStatus
from view.tasks.tasks_info import TasksInfo
from view.error import Error as ErrorView


from controller.case import Case as CaseController
from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)

from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderConfigurationController,
)


from common.constants.view import general
from common.constants.view.web import *

from common.config import LogConfigTools
from common.utility import resolve_path, get_version

from ui.web import resources


class Web(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Web, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.screenshot_directory = None
        self.acquisition_status = AcquisitionStatus.UNSTARTED

        self.log_confing = LogConfigTools()
        self.case_info = None
        self.web_engine_view = None

        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/web/web.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # CUSTOM TOP BAR
        self.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.close_button.clicked.connect(self.close)

        # CONFIGURATION BUTTON
        self.configuration_button.clicked.connect(show_configuration_dialog)

        # ACQUISITION INFO BUTTON
        self.acquisition_info.clicked.connect(show_acquisition_info_dialog)

        # HIDE PROGRESS BAR
        self.progress_bar.setHidden(True)

        # HIDE STATUS MESSAGE
        self.status_message.setHidden(True)

        # SET VERSION
        self.version.setText("v" + get_version())

        # SET NAVIGATION BUTTONS
        self.back_button.clicked.connect(self.__back)
        self.forward_button.clicked.connect(self.__forward)
        self.reload_button.clicked.connect(self.__reload)
        self.home_button.clicked.connect(self.__navigate_home)
        self.url_line_edit.returnPressed.connect(self.__navigate_to_url)
        self.stop_button.clicked.connect(self.__stop_load_url)

        # SET ACQUISITON BUTTONS
        self.start_acquisition_button.clicked.connect(self.__start_acquisition)
        self.stop_acquisition_button.clicked.connect(self.__stop_acquisition)
        self.screenshot_visible_area_button.clicked.connect(self.__take_screenshot)
        self.screenshot_selected_area_button.clicked.connect(
            self.__take_screenshot_selected_area
        )
        self.screenshot_full_page_button.clicked.connect(
            self.__take_full_page_screenshot
        )

        self.tabs.clear()

        # Since 1.3.0 I disabled multitab managment, but I left these methods in case I wanted to re-enable multitab
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.__enable_all()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def init(self, case_info, wizard, options=None):
        self.wizard = wizard
        self.case_info = case_info

        self.case_button.clicked.connect(lambda: show_case_info_dialog(self.case_info))

        # ACQUISITION
        self.acquisition_manager = WebAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status_message,
            self,
        )

        self.acquisition_manager.start_tasks_is_finished.connect(
            self.__start_tasks_is_finished
        )
        self.acquisition_manager.stop_tasks_is_finished.connect(
            self.__stop_tasks_is_finished
        )
        self.acquisition_manager.post_acquisition_is_finished.connect(
            self.__post_acquisition_is_finished
        )
        self.acquisition_manager.task_screenrecorder_is_finished.connect(
            self.__task_screenrecorder_is_finished
        )

        self.__add_new_tab(
            QtCore.QUrl(
                GeneralConfigurationController().configuration["home_page_url"]
            ),
            "Homepage",
        )

    def __start_acquisition(self):
        self.acquisition_status = AcquisitionStatus.STARTED

        self.acquisition_directory = CaseController().create_acquisition_directory(
            "web",
            GeneralConfigurationController().configuration["cases_folder_path"],
            self.case_info["name"],
            self.tabs.currentWidget().url().toString(),
        )

        if self.acquisition_directory is not None:
            self.tabs.currentWidget().set_acquisition_dir(self.acquisition_directory)

            self.screenshot_directory = os.path.join(
                self.acquisition_directory, "screenshot"
            )
            if not os.path.isdir(self.screenshot_directory):
                os.makedirs(self.screenshot_directory)

            # show progress bar
            self.progress_bar.setHidden(False)
            self.status_message.setHidden(False)

            self.__enable_all()

            self.acquisition_manager.options = {
                "acquisition_directory": self.acquisition_directory,
                "screenshot_directory": self.screenshot_directory,
                "type": "web",
                "case_info": self.case_info,
                "current_widget": self.tabs.currentWidget(),
                "exclude_from_hash_calculation": [
                    ScreenRecorderConfigurationController().options["filename"]
                ],
            }

            self.acquisition_manager.load_tasks()
            self.acquisition_manager.start()

    def __start_tasks_is_finished(self):
        self.acquisition_manager.set_completed_progress_bar()
        self.status_message.setText("")

        # show progress bar for 2 seconds
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(2000, loop.quit)
        loop.exec()

        self.progress_bar.setHidden(True)
        self.progress_bar.setValue(0)

        self.__enable_all()

        self.progress_bar.setHidden(True)

    def __stop_acquisition(self):
        self.acquisition_status = AcquisitionStatus.STOPED
        self.__enable_all()
        self.progress_bar.setHidden(False)
        url = self.tabs.currentWidget().url().toString()

        self.acquisition_manager.options["url"] = url
        self.acquisition_manager.options["current_widget"] = self.tabs.currentWidget()

        self.acquisition_manager.stop()

    def __stop_tasks_is_finished(self):
        self.acquisition_manager.start_post_acquisition()

    def __post_acquisition_is_finished(self):
        self.acquisition_manager.stop_screen_recorder()

    def __task_screenrecorder_is_finished(self):
        self.acquisition_status = AcquisitionStatus.UNSTARTED

        self.tabs.currentWidget().reconnect_signal()
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        # hidden progress bar
        self.progress_bar.setHidden(True)
        self.status_message.setText("")

        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()

        try:
            self.tabs.currentWidget().saveResourcesFinished.disconnect()
        except TypeError:
            pass

        self.__enable_all()
        show_finish_acquisition_dialog(self.acquisition_directory)

    def __enable_all(self):
        if self.acquisition_status == AcquisitionStatus.UNSTARTED:
            self.__enable_screenshot_buttons(False)
            self.__enable_navigation_buttons(True)
            self.setEnabled(True)
        elif self.acquisition_status == AcquisitionStatus.STARTED:
            self.__enable_screenshot_buttons(True)
            self.__enable_navigation_buttons(True)
            self.setEnabled(True)
        elif self.acquisition_status == AcquisitionStatus.STOPED:
            self.setEnabled(False)

        self.__enable_acquisition_buttons()

    def __enable_acquisition_buttons(self):
        if self.acquisition_status == AcquisitionStatus.UNSTARTED:
            stop = False
            start = status = True
        elif self.acquisition_status == AcquisitionStatus.STARTED:
            start = False
            stop = status = True
        elif self.acquisition_status == AcquisitionStatus.STOPED:
            stop = status = start = False

        self.start_acquisition_button.setEnabled(start)
        self.stop_acquisition_button.setEnabled(stop)

    def __enable_screenshot_buttons(self, enable):
        self.screenshot_visible_area_button.setEnabled(enable)
        self.screenshot_selected_area_button.setEnabled(enable)
        self.screenshot_full_page_button.setEnabled(enable)

    def __enable_navigation_buttons(self, enable):
        self.back_button.setEnabled(enable)
        self.forward_button.setEnabled(enable)
        self.reload_button.setEnabled(enable)
        self.home_button.setEnabled(enable)
        self.url_line_edit.setEnabled(enable)
        self.stop_button.setEnabled(enable)

    def __take_screenshot(self):
        if self.screenshot_directory is not None:
            self.setEnabled(False)
            filename = screenshot_filename(
                self.screenshot_directory, self.tabs.currentWidget().url().host()
            )
            self.tabs.currentWidget().grab().save(filename)
            self.setEnabled(True)

    def __take_screenshot_selected_area(self):
        if self.screenshot_directory is not None:
            self.setEnabled(False)
            filename = screenshot_filename(
                self.screenshot_directory,
                "selected_" + self.tabs.currentWidget().url().host(),
            )
            select_area = SelectAreaScreenshot(filename, self)
            select_area.finished.connect(self.__enable_all)
            select_area.snip_area()

    def __take_full_page_screenshot(self):
        FullPageScreenShot(
            self.tabs.currentWidget(),
            self.acquisition_directory,
            self.screenshot_directory,
            self,
        ).take_screenshot()

    def __back(self):
        self.tabs.currentWidget().back()

    def __forward(self):
        self.tabs.currentWidget().forward()

    def __reload(self):
        self.tabs.currentWidget().reload()

    def __add_new_tab(self, qurl=None, label="Blank", page=None):
        if qurl is None:
            qurl = QtCore.QUrl("")
        self.web_engine_view = WebEngineView()

        user_agent = GeneralConfigurationController().configuration["user_agent"]
        self.web_engine_view.page().profile().setHttpUserAgent(
            user_agent + " FreezingInternetTool/" + get_version()
        )

        if page is None:
            page = WebEnginePage(self.web_engine_view)

        page.certificateError.connect(page.handleCertificateError)

        page.new_page_after_link_with_target_blank_attribute.connect(
            lambda page: self.__add_new_tab(page=page)
        )
        self.web_engine_view.setPage(page)

        self.web_engine_view.setUrl(qurl)
        i = self.tabs.addTab(self.web_engine_view, label)

        self.tabs.setCurrentIndex(i)

        # More difficult! We only want to update the url when it's from the
        # correct tab
        self.web_engine_view.urlChanged.connect(
            lambda qurl, browser=self.web_engine_view: self.__update_urlbar(
                qurl, browser
            )
        )

        self.web_engine_view.loadProgress.connect(self.__load_progress)

        self.web_engine_view.loadFinished.connect(
            lambda _, i=i, browser=self.web_engine_view: self.__page_on_loaded(
                i, browser
            )
        )

        self.web_engine_view.urlChanged.connect(
            lambda qurl: self.__allow_notifications(qurl)
        )

        self.web_engine_view.downloadItemFinished.connect(
            self.__handle_download_item_finished
        )

        if i == 0:
            self.showMaximized()

    def __handle_download_item_finished(self, filename):
        self.status_message.setText(general.DOWNLOAD + ": " + filename)
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(2000, loop.quit)
        loop.exec()
        self.status_message.setText("")

    def __page_on_loaded(self, tab_index, browser):
        self.tabs.setTabText(tab_index, browser.page().title())

    def tab_open_doubleclick(self, i):
        if i == -1 and self.isEnabled():  # No tab under the click
            self.add_new_tab()

    def current_tab_changed(self, i):
        self.tabs.currentWidget().page().profile().disconnect()  # Disconnect the current tab
        for index in range(self.tabs.count()):
            if self.tabs.widget(index) == self.tabs.currentWidget():
                self.tabs.currentWidget().reconnect()  # Reconnect only the new current tab

        if self.tabs.currentWidget() is not None:
            qurl = self.tabs.currentWidget().url()
            self.__update_urlbar(qurl, self.tabs.currentWidget())
            self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()

    def __navigate_home(self):
        self.tabs.currentWidget().setUrl(
            QtCore.QUrl(GeneralConfigurationController().configuration["home_page_url"])
        )

    def __navigate_to_url(self):  # Does not receive the Url
        q = QtCore.QUrl(self.url_line_edit.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def __stop_load_url(self):
        self.tabs.currentWidget().stop()

    def __load_progress(self, progress):
        if progress == 100:
            pass

    def __update_urlbar(self, q, browser=None):
        pass

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == "https":
            # Secure padlock icon
            pixmap = QtGui.QPixmap(
                os.path.join(resolve_path("ui/images/toolbar"), "lock-close.png")
            )
            self.httpsIcon.setPixmap(pixmap)

        else:
            # Insecure padlock icon
            pixmap = QtGui.QPixmap(
                os.path.join(resolve_path("ui/images/toolbar"), "lock-open.png")
            )
            self.httpsIcon.setPixmap(pixmap)

        self.url_line_edit.setText(q.toString())
        self.url_line_edit.setCursorPosition(0)

    def __allow_notifications(self, q):
        feature = QWebEnginePage.Feature.Notifications
        permission = QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        self.web_engine_view.page().setFeaturePermission(q, feature, permission)

    def __back_to_wizard(self):
        if self.acquisition_status == AcquisitionStatus.UNSTARTED:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()
        else:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Warning,
                ACQUISITION_IS_RUNNING,
                WAR_ACQUISITION_IS_RUNNING,
                "",
            )
            error_dlg.exec()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
