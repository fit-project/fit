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

import subprocess

import numpy as np
from PIL import Image

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from view.scrapers.web.web_engine_view import WebEngineView, WebEnginePage

from view.scrapers.web.navigationtoolbar import (
    NavigationToolBar as NavigationToolBarView,
)
from view.scrapers.web.selected_area_screenshot import SelectAreaScreenshot
from view.scrapers.web.full_page_screenshot import FullPageScreenShot
from view.scrapers.web.acquisition import WebAcquisition
from view.tasks.tasks_info import TasksInfo
from view.menu_bar import MenuBar as MenuBarView
from view.error import Error as ErrorView


from common.constants.view import general
from common.constants.view.web import *
from common.constants import logger, details


from common.config import LogConfigTools
from common.utility import screenshot_filename, get_version, get_platform, resolve_path


class Web(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Web, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.screenshot_directory = None
        self.acquisition_is_running = False

        self.log_confing = LogConfigTools()
        self.case_info = None
        self.web_engine_view = None

        self.setWindowFlag(QtCore.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setObjectName("FITWeb")
        self.setWindowTitle("Freezing Internet Tool")
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg"))
        )

    def init(self, case_info, wizard, options=None):
        self.wizard = wizard
        self.case_info = case_info

        #### - START MENU BAR - #####
        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        # This bar is common on all main window
        self.menu_bar = MenuBarView(self, self.case_info)

        # Add custom menu on menu bar
        tab_menu = self.menu_bar.addMenu("&Tab")
        new_tab_action = QtGui.QAction(
            QtGui.QIcon(
                os.path.join(resolve_path("assets/images"), "ui-tab--plus.png")
            ),
            "New Tab",
            self,
        )
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        tab_menu.addAction(new_tab_action)

        # Add default menu on menu bar
        self.menu_bar.add_default_actions()
        self.setMenuBar(self.menu_bar)
        #### - END MENUBAR - #####

        #### - START NAVIGATION TOOL BAR - #####
        self.navtb = NavigationToolBarView(self)
        self.addToolBar(self.navtb)
        #### - END NAVIGATION TOOL BAR - #####

        #### - START STATUS BAR - #####
        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.progress_bar.setFixedHeight(25)
        self.status.addPermanentWidget(self.progress_bar)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setStatusBar(self.status)
        self.progress_bar.setHidden(True)
        #### - END STATUS BAR - #####

        # TABS BAR
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        # ACQUISITION
        self.acquisition_manager = WebAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status,
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

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

        self.configuration_screenrecorder = (
            self.menu_bar.configuration_view.get_tab_from_name(
                "configuration_screenrecorder"
            )
        )

        self.add_new_tab(
            QtCore.QUrl(self.configuration_general.configuration["home_page_url"]),
            "Homepage",
        )

    def start_acquisition(self):
        self.acquisition_is_running = True

        self.acquisition_directory = (
            self.menu_bar.case_view.form.controller.create_acquisition_directory(
                "web",
                self.configuration_general.configuration["cases_folder_path"],
                self.case_info["name"],
                self.tabs.currentWidget().url().toString(),
            )
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

            self.__disable_all()

            self.acquisition_manager.options = {
                "acquisition_directory": self.acquisition_directory,
                "screenshot_directory": self.screenshot_directory,
                "type": "web",
                "case_info": self.case_info,
                "current_widget": self.tabs.currentWidget(),
                "exclude_from_hash_calculation": [
                    self.configuration_screenrecorder.options["filename"]
                ],
            }

            self.acquisition_manager.load_tasks()
            self.acquisition_manager.start()

    def __start_tasks_is_finished(self):
        self.acquisition_manager.set_completed_progress_bar()
        self.status.showMessage("")

        # show progress bar for 2 seconds
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(2000, loop.quit)
        loop.exec()

        self.progress_bar.setHidden(True)
        self.progress_bar.setValue(0)

        self.__enable_all()

        self.menu_bar.enable_actions(False)
        # disable start acquisition button
        self.navtb.enable_start_acquisition_button()
        # enable screenshot buttons
        self.navtb.enable_screenshot_buttons()
        # enable stop and info acquisition button
        self.navtb.enable_stop_and_info_acquisition_button()

        self.progress_bar.setHidden(True)

    def stop_acquisition(self):
        self.progress_bar.setHidden(False)
        url = self.tabs.currentWidget().url().toString()
        self.__disable_all()

        self.acquisition_manager.options["url"] = url
        self.acquisition_manager.options["current_widget"] = self.tabs.currentWidget()

        self.acquisition_manager.stop()

    def __stop_tasks_is_finished(self):
        self.acquisition_manager.start_post_acquisition()

    def __post_acquisition_is_finished(self):
        self.acquisition_manager.stop_screen_recorder()

    def __task_screenrecorder_is_finished(self):
        self.acquisition_is_running = False

        self.tabs.currentWidget().reconnect_signal()
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        # hidden progress bar
        self.progress_bar.setHidden(True)
        self.status.showMessage("")

        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()

        try:
            self.tabs.currentWidget().saveResourcesFinished.disconnect()
        except TypeError:
            pass

        self.__enable_all()
        self.__show_finish_acquisition_dialog()

    def acquisition_info(self):
        TasksInfo(self).show()

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(logger.ACQUISITION_FINISHED)
        msg.setText(details.ACQUISITION_FINISHED)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
        )

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__open_acquisition_directory()

    def __open_acquisition_directory(self):
        platform = get_platform()

        if platform == "win":
            os.startfile(self.acquisition_directory)
        elif platform == "osx":
            subprocess.call(["open", self.acquisition_directory])
        else:  # platform == 'lin' || platform == 'other'
            subprocess.call(["xdg-open", self.acquisition_directory])

    def __disable_all(self):
        self.setEnabled(False)
        self.navtb.setEnabled(False)
        self.navtb.enable_actions(enabled=False)

    def __enable_all(self):
        self.setEnabled(True)
        self.navtb.setEnabled(True)

        # re-enable configuration and case menu
        self.menu_bar.enable_actions(True)

        # Add information button to re-enable buttons list
        self.navtb.navigation_actions.append("info")
        self.navtb.enable_actions(filter=self.navtb.navigation_actions)
        self.navtb.enable_screenshot_buttons()
        self.navtb.enable_start_acquisition_button()
        self.navtb.enable_stop_and_info_acquisition_button()

    def take_screenshot(self):
        if self.screenshot_directory is not None:
            self.__disable_all()
            filename = screenshot_filename(
                self.screenshot_directory, self.tabs.currentWidget().url().host()
            )
            self.tabs.currentWidget().grab().save(filename)
            self.__enable_all()

    def take_screenshot_selected_area(self):
        if self.screenshot_directory is not None:
            self.__disable_all()
            filename = screenshot_filename(
                self.screenshot_directory,
                "selected_" + self.tabs.currentWidget().url().host(),
            )
            select_area = SelectAreaScreenshot(filename, self)
            select_area.finished.connect(self.__enable_all)
            select_area.snip_area()

    def take_full_page_screenshot(self):
        FullPageScreenShot(
            self.tabs.currentWidget(),
            self.acquisition_directory,
            self.screenshot_directory,
            self,
        ).take_screenshot()

    def back(self):
        self.tabs.currentWidget().back()

    def forward(self):
        self.tabs.currentWidget().forward()

    def reload(self):
        self.tabs.currentWidget().reload()

    def add_new_tab(self, qurl=None, label="Blank", page=None):
        if qurl is None:
            qurl = QtCore.QUrl("")
        self.web_engine_view = WebEngineView()

        user_agent = self.configuration_general.configuration["user_agent"]
        self.web_engine_view.page().profile().setHttpUserAgent(
            user_agent + " FreezingInternetTool/" + get_version()
        )

        if page is None:
            page = WebEnginePage(self.web_engine_view)

        page.certificateError.connect(page.handleCertificateError)

        page.new_page_after_link_with_target_blank_attribute.connect(
            lambda page: self.add_new_tab(page=page)
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

        self.web_engine_view.loadProgress.connect(self.load_progress)

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
        self.status.showMessage(general.DOWNLOAD + ": " + filename)
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(2000, loop.quit)
        loop.exec()
        self.status.showMessage("")

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
        self.setWindowTitle("%s - Freezing Internet Tool" % title)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(
            QtCore.QUrl(self.configuration_general.configuration["home_page_url"])
        )

    def navigate_to_url(self):  # Does not receive the Url
        q = QtCore.QUrl(self.navtb.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def load_progress(self, progress):
        if progress == 100:
            self.navtb.enable_screenshot_buttons()

    def __update_urlbar(self, q, browser=None):
        self.navtb.enable_screenshot_buttons()

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == "https":
            # Secure padlock icon
            pixmap = QtGui.QPixmap(
                os.path.join(resolve_path("assets/svg/toolbar"), "lock-close.svg")
            )
            self.navtb.httpsicon.setPixmap(
                pixmap.scaled(
                    16, 16, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )
            )

        else:
            # Insecure padlock icon
            pixmap = QtGui.QPixmap(
                os.path.join(resolve_path("assets/svg/toolbar"), "lock-open.svg")
            )
            self.navtb.httpsicon.setPixmap(
                pixmap.scaled(
                    16, 16, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )
            )

        self.navtb.urlbar.setText(q.toString())
        self.navtb.urlbar.setCursorPosition(0)

    def __allow_notifications(self, q):
        feature = QWebEnginePage.Feature.Notifications
        permission = QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        self.web_engine_view.page().setFeaturePermission(q, feature, permission)

    def __back_to_wizard(self):
        if self.acquisition_is_running is False:
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
