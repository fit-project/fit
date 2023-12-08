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
from PyQt6.QtWidgets import QListWidgetItem, QCheckBox

from view.scrapers.entire_website.form import EntireWebsiteForm
from view.scrapers.entire_website.acquisition import EntireWebsiteAcquisition


from view.menu_bar import MenuBar as MenuBarView

from view.error import Error as ErrorView
from view.spinner import Spinner


from common.constants.view.tasks import status
from common.constants import details, logger

from common.constants.view import general, entire_site
from common.utility import get_platform


class EntireWebsite(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(EntireWebsite, self).__init__(*args, **kwargs)
        self.spinner = Spinner()

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.selected_urls = None
        self.wizard = wizard
        self.case_info = case_info

        self.setWindowIcon(QtGui.QIcon(os.path.join("assets/svg/", "FIT.svg")))

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        self.width = 990
        self.height = 480
        self.setFixedSize(self.width, self.height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setStyleSheet(
            "QWidget {background-color: rgb(255, 255, 255);}"
        )
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

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)

        self.form = EntireWebsiteForm(self.centralwidget)

        self.form.load_website_button.clicked.connect(self.__load_website)
        self.form.add_button.clicked.connect(self.__add_url)

        # SELECT/DESELECT BUTTON
        self.selector_button = QtWidgets.QPushButton(self)
        self.selector_button.setGeometry(QtCore.QRect(515, 410, 75, 25))
        self.selector_button.setObjectName("selector_button")
        self.selector_button.setFont(font)
        self.selector_button.setEnabled(False)
        self.selector_button.clicked.connect(self.__select)

        # SCRAPE BUTTON
        self.scrape_button = QtWidgets.QPushButton(self)
        self.scrape_button.setGeometry(QtCore.QRect(875, 410, 70, 25))
        self.scrape_button.setObjectName("scrapeButton")
        self.scrape_button.setFont(font)
        self.scrape_button.clicked.connect(self.__download)
        self.scrape_button.setEnabled(False)

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

        self.acquisition_manager = EntireWebsiteAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status,
            self,
        )

        self.acquisition_manager.start_tasks_is_finished.connect(
            self.__start_task_is_finished
        )

        self.acquisition_manager.valid_url.connect(self.__is_valid_url)
        self.acquisition_manager.progress.connect(self.__handle_progress)
        self.acquisition_manager.sitemap_finished.connect(self.__get_sitemap_finished)
        self.acquisition_manager.post_acquisition_is_finished.connect(
            self.__acquisition_is_finished
        )

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.scrape_button.setText(general.DOWNLOAD)
        self.selector_button.setText(entire_site.DESELECT)

    def __load_website(self):
        self.__enable_all(False)
        self.__start_spinner()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.options["start_url"] = self.form.input_url.text()
            self.acquisition_manager.check_is_valid_url(self.form.input_url.text())

    def __is_valid_url(self, __status):
        if __status == status.SUCCESS:
            if self.acquisition_manager.caller_function_name == "__load_website":
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(1000, loop.quit)
                loop.exec()
                self.acquisition_manager.get_sitemap()
            elif self.acquisition_manager.caller_function_name == "__add_url":
                self.__add_url(True)
        else:
            self.spinner.stop()
            self.__enable_all(True)

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = (
                self.menu_bar.case_view.form.controller.create_acquisition_directory(
                    "entire_website",
                    self.configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                    self.form.input_url.text(),
                )
            )

        if self.acquisition_directory is not None:
            if self.is_task_started is False:
                self.acquisition_manager.options = {
                    "acquisition_directory": self.acquisition_directory,
                    "type": "entire_website",
                    "case_info": self.case_info,
                }
                self.acquisition_manager.load_tasks()
                self.acquisition_manager.start()

    def __start_task_is_finished(self):
        self.is_task_started = True
        self.__load_website()

    def __handle_progress(self):
        self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

    def __get_sitemap_finished(self, __status, urls):
        self.spinner.stop()
        self.__enable_all(True)
        if __status == status.SUCCESS:
            if len(urls) == 0:
                pass
                error_dlg = ErrorView(
                    QtWidgets.QMessageBox.Icon.Information,
                    entire_site.NO_URLS_FOUND,
                    entire_site.NO_URLS_FOUND_MSG.format(
                        self.acquisition_manager.options.get("start_url")
                    ),
                    details.CHECK_URL,
                )
                error_dlg.exec()
            else:
                self.form.list_widget.clear()
                for url in sorted(urls):
                    item = QListWidgetItem()
                    check_box = QCheckBox(url)
                    item.setSizeHint(check_box.sizeHint())
                    check_box.setChecked(True)
                    self.form.list_widget.addItem(item)
                    self.form.list_widget.setItemWidget(item, check_box)

                self.scrape_button.setEnabled(True)
                self.selector_button.setEnabled(True)
                self.form.enable_custom_urls(True)

    def __select(self):
        if self.selector_button.text() == entire_site.DESELECT:
            self.selector_button.setText(entire_site.SELECT)
            for index in range(self.form.list_widget.count()):
                item = self.form.list_widget.item(index)
                if isinstance(item, QListWidgetItem):
                    widget = self.form.list_widget.itemWidget(item)
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(False)
        else:
            self.selector_button.setText(entire_site.DESELECT)
            for index in range(self.form.list_widget.count()):
                item = self.form.list_widget.item(index)
                if isinstance(item, QListWidgetItem):
                    widget = self.form.list_widget.itemWidget(item)
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(True)

    def __add_url(self, __is_valid_url=False):
        self.__enable_all(False)
        self.__start_spinner()
        if __is_valid_url is False:
            self.acquisition_manager.check_is_valid_url(
                self.form.input_custom_url.text()
            )
        else:
            if not self.__item_exists_in_list_widget(
                self.form.list_widget, self.form.input_custom_url.text()
            ):
                item = QListWidgetItem()
                check_box = QCheckBox(self.form.input_custom_url.text())
                item.setSizeHint(check_box.sizeHint())
                check_box.setChecked(True)
                self.form.list_widget.addItem(item)
                self.form.list_widget.setItemWidget(item, check_box)

            self.spinner.stop()
            self.__enable_all(True)

    def __item_exists_in_list_widget(self, list_widget, text):
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if isinstance(item, QListWidgetItem):
                widget = list_widget.itemWidget(item)
                if isinstance(widget, QCheckBox):
                    if widget.text() == text:
                        return True
        return False

    def __download(self):
        self.__enable_all(False)
        self.__start_spinner()
        self.is_acquisition_running = True
        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)

        self.selected_urls = []
        for row in range(self.form.list_widget.count()):
            item = self.form.list_widget.item(row)
            check_box = self.form.list_widget.itemWidget(item)
            if check_box.isChecked():
                self.selected_urls.append(check_box.text())

        self.increment = 100 / len(self.selected_urls)

        self.acquisition_manager.options["urls"] = self.selected_urls
        self.acquisition_manager.download()

    def __acquisition_is_finished(self):
        self.spinner.stop()
        self.__enable_all(True)
        self.form.list_widget.clear()
        self.form.input_custom_url.setText("")
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        self.progress_bar.setHidden(True)
        self.status.showMessage("")

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False

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

    def __enable_all(self, enable):
        self.setEnabled(enable)

    def __start_spinner(self):
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
