# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import logging


from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtWidgets import QListWidgetItem, QCheckBox

from view.scrapers.entire_website.acquisition import EntireWebsiteAcquisition


from view.error import Error as ErrorView
from view.spinner import Spinner
from view.util import (
    show_configuration_dialog,
    show_case_info_dialog,
    show_finish_acquisition_dialog,
    show_acquisition_info_dialog,
)

from controller.case import Case as CaseController
from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)

from common.constants.view.tasks import status
from common.constants import details

from common.constants.view import entire_site
from common.utility import resolve_path, get_version


class EntireWebsite(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(EntireWebsite, self).__init__(*args, **kwargs)
        self.spinner = Spinner()
        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/entire_website/entire_website.ui"), self)

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
        self.progress_bar.setValue(0)
        self.progress_bar.setHidden(True)

        # HIDE STATUS MESSAGE
        self.status_message.setHidden(True)

        # SET VERSION
        self.version.setText("v" + get_version())

        # LOAD FROM DOMAIN CHECKBOX
        self.load_from_domain.clicked.connect(self.__switch_load_type)

        # LOAD FROM SITEMAP CHECKBOX
        self.load_from_sitemap.clicked.connect(self.__switch_load_type)

        self.load_website_button.setEnabled(False)
        self.input_url.textChanged.connect(
            lambda: self.__enable_button(self.input_url, self.load_website_button)
        )

        self.add_custom_url.setEnabled(False)
        self.input_custom_url.textChanged.connect(
            lambda: self.__enable_button(self.input_custom_url, self.add_url_button)
        )

        self.right_content.setEnabled(False)

        # CHECK UNCHECK ALL
        self.check_uncheck_all.stateChanged.connect(self.__check_uncheck_all)

        self.url_list.clear()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def __switch_load_type(self):
        self.input_url.setText("")
        if self.sender().objectName() == "load_from_domain":
            self.input_url.setPlaceholderText(entire_site.PLACEHOLDER_URL)
            self.load_from_domain.setChecked(True)
            self.load_from_sitemap.setChecked(False)
        elif self.sender().objectName() == "load_from_sitemap":
            self.input_url.setPlaceholderText(entire_site.PLACEHOLDER_SITEMAP_URL)
            self.load_from_domain.setChecked(False)
            self.load_from_sitemap.setChecked(True)

    def __enable_button(self, input, button):
        all_field_filled = bool(input.text())
        button.setEnabled(all_field_filled)

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.selected_urls = None
        self.wizard = wizard
        self.case_info = case_info

        self.case_button.clicked.connect(lambda: show_case_info_dialog(self.case_info))

        self.load_website_button.clicked.connect(self.__load_website)
        self.add_url_button.clicked.connect(self.__add_url)
        # self.form.selector_button.clicked.connect(self.__select)
        self.download_button.clicked.connect(self.__download)

        self.acquisition_manager = EntireWebsiteAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status_message,
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

    def __load_website(self):
        self.url_list.clear()
        self.input_custom_url.clear()
        self.progress_bar.setHidden(False)
        self.status_message.setHidden(False)
        self.__enable_all(False)
        self.__start_spinner()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.check_is_valid_url(self.input_url.text())

    def __is_valid_url(self, __status):
        if __status == status.SUCCESS:
            if self.acquisition_manager.caller_function_name == "__load_website":
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(1000, loop.quit)
                loop.exec()
                self.acquisition_manager.options["start_url"] = self.input_url.text()

                for checkbox in self.url_configuration.findChildren(
                    QtWidgets.QCheckBox
                ):
                    if checkbox.isChecked():
                        self.acquisition_manager.options["load_type"] = (
                            checkbox.objectName()
                        )

                self.acquisition_manager.get_sitemap()
            elif self.acquisition_manager.caller_function_name == "__add_url":
                self.__add_url(True)
        else:
            self.spinner.stop()
            self.__enable_all(True)

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = CaseController().create_acquisition_directory(
                "entire_website",
                GeneralConfigurationController().configuration["cases_folder_path"],
                self.case_info["name"],
                self.input_url.text(),
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
        self.progress_bar.setHidden(True)
        self.status_message.setHidden(True)
        if __status == status.SUCCESS:
            if len(urls) == 0:
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
                self.check_uncheck_all.setChecked(True)
                for url in sorted(urls):
                    item = QListWidgetItem()
                    check_box = QCheckBox(url)
                    item.setSizeHint(QtCore.QSize(check_box.width(), 25))
                    check_box.setChecked(True)
                    self.url_list.addItem(item)
                    self.url_list.setItemWidget(item, check_box)

                self.add_custom_url.setEnabled(True)
                self.right_content.setEnabled(True)

    def __check_uncheck_all(self):
        if self.check_uncheck_all.isChecked() is False:
            for index in range(self.url_list.count()):
                item = self.url_list.item(index)
                if isinstance(item, QListWidgetItem):
                    widget = self.url_list.itemWidget(item)
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(False)
        else:
            for index in range(self.url_list.count()):
                item = self.url_list.item(index)
                if isinstance(item, QListWidgetItem):
                    widget = self.url_list.itemWidget(item)
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(True)

    def __add_url(self, __is_valid_url=False):
        self.__enable_all(False)
        self.__start_spinner()
        if __is_valid_url is False:
            self.acquisition_manager.check_is_valid_url(self.input_custom_url.text())
        else:
            if not self.__item_exists_in_list_widget(
                self.url_list, self.input_custom_url.text()
            ):
                item = QListWidgetItem()
                check_box = QCheckBox(self.input_custom_url.text())
                item.setSizeHint(check_box.sizeHint())
                check_box.setChecked(True)
                self.url_list.addItem(item)
                self.url_list.setItemWidget(item, check_box)

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
        self.status_message.setHidden(False)

        self.selected_urls = []
        for row in range(self.url_list.count()):
            item = self.url_list.item(row)
            check_box = self.url_list.itemWidget(item)
            if check_box.isChecked():
                self.selected_urls.append(check_box.text())

        if len(self.selected_urls) > 0:
            self.increment = 100 / len(self.selected_urls)

        self.acquisition_manager.options["urls"] = self.selected_urls
        self.acquisition_manager.download()

    def __acquisition_is_finished(self):
        self.spinner.stop()
        self.__enable_all(True)
        self.add_custom_url.setEnabled(False)
        self.right_content.setEnabled(False)
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        self.progress_bar.setHidden(True)
        self.status_message.setHidden(True)
        self.status_message.setText("")

        show_finish_acquisition_dialog(self.acquisition_directory)

        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False

    def __enable_all(self, enable):
        self.setEnabled(enable)

    def __start_spinner(self):
        center_x = self.x() + self.width() / 2
        center_y = self.y() + self.height() / 2
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
