#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtCore, QtWidgets, uic

from view.case_form_manager import CaseFormManager
from view.error import Error as ErrorView

from view.verify_pec import VerifyPec as VerifyPecView
from view.verify_pdf_timestamp import VerifyPDFTimestamp as VerifyPDFTimestampView

from view.util import show_configuration_dialog, show_case_info_dialog

from common.constants import error
from common.constants.view import wizard
from common.utility import resolve_path, get_version


from ui.wizard import resources


class Wizard(QtWidgets.QMainWindow):
    finished = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        uic.loadUi(resolve_path("ui/wizard/wizard.ui"), self)

        self.selcted_task = None
        self.case_info = {}

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

        # VERIFY TIMESTAMP BUTTON
        self.verify_timestamp_button.clicked.connect(self.__verify_timestamp)

        # VERIFY PEC BUTTON
        self.verify_pec_button.clicked.connect(self.__verify_pec)

        # PAGES
        self.pages.setCurrentIndex(0)

        # NEXT BUTTON
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.__next_page)

        # BACK BUTTON
        self.back_button.clicked.connect(self.__back_page)
        self.back_button.hide()

        # SET VERSION
        self.version.setText("v" + get_version())

        # PAGE1 CASE INFO FORM
        self.form_manager = CaseFormManager(self.form)
        self.form_manager.name.currentTextChanged.connect(self.__enable_next_button)

        # PAGE2 SELECT TASK
        self.tasks = self.findChildren(QtWidgets.QCheckBox)

        for task in self.tasks:
            task.setAttribute(QtCore.Qt.WidgetAttribute.WA_MacShowFocusRect, 0)
            task.clicked.connect(self.__task_clicked)

        # SUMMARY BUTTON
        self.case_summary_button.clicked.connect(show_case_info_dialog)
        self.case_summary_button.hide()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def __next_page(self):
        if self.pages.currentIndex() == 0:
            self.pages.setCurrentIndex(self.pages.currentIndex() + 1)
            self.back_button.show()

            if self.pages.currentIndex() == self.pages.count() - 1:
                self.__load_case_info()
                self.next_button.setText("Start")
                self.next_button.setEnabled(False)

        elif self.pages.currentIndex() == self.pages.count() - 1:
            self.__start()

    def __back_page(self):

        if self.pages.currentIndex() > 0:
            self.pages.setCurrentIndex(self.pages.currentIndex() - 1)
            self.next_button.setText("Next >")
            self.__enable_next_button()

        if self.pages.currentIndex() == 0:
            self.__unchecked_tasks()
            self.back_button.hide()

    def __verify_timestamp(self):
        verify_timestamp = VerifyPDFTimestampView()
        verify_timestamp.init(self.case_info, self)
        verify_timestamp.show()

    def __verify_pec(self):
        verify_pec = VerifyPecView(self)
        verify_pec.show()

    def reload_case_info(self):
        self.form_manager.set_case_information()

    def __load_case_info(self):
        self.case_info = self.form_manager.get_current_case_info()

    def __enable_next_button(self):
        if self.form_manager.name.currentText():
            self.next_button.setEnabled(True)
        else:
            self.next_button.setEnabled(False)

    def __unchecked_tasks(self):
        for task in self.tasks:
            task.setChecked(False)

    def __task_clicked(self):
        if self.sender().isChecked():
            for task in self.tasks:
                if task.isChecked() and task != self.sender():
                    task.setChecked(False)

            self.next_button.setEnabled(True)
            self.selcted_task = self.sender().objectName()
        else:
            self.next_button.setEnabled(False)
            self.selcted_task = None

    def __start(self):
        # store information case on the local DB
        try:
            if "id" in self.case_info:
                self.form_manager.controller.cases = self.case_info
            else:
                self.case_info = self.form_manager.controller.add(self.case_info)
                self.form_manager.set_current_cases()
                self.form_manager.set_index_from_case_id(self.case_info["id"])
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Warning,
                wizard.INSERT_UPDATE_CASE_INFO,
                error.INSERT_UPDATE_CASE_INFO,
                str(e),
            )
            error_dlg.exec()

        # Send signal to main loop to start the acquisition window
        self.finished.emit(self.selcted_task, self.case_info)
        self.hide()
