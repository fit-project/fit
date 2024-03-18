#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os

from configparser import ConfigParser

from PyQt6 import QtCore, QtWidgets, QtGui, uic

from _ui.wizard import resources


from view.configuration import Configuration as ConfigurationView
from view.case_form_manager import CaseFormManager
from view.case_form_dialog import CaseFormDialog
from view.error import Error as ErrorView

from common.utility import resolve_path

from common.constants.view.wizard import *
from common.constants import error
from common.constants.view import wizard, general


# os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class Wizard(QtWidgets.QMainWindow):
    finished = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        uic.loadUi(resolve_path("_ui/wizard/wizard.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # SETTING BUTTON
        self.configuration_button = self.findChild(
            QtWidgets.QPushButton, "settingsTopButton"
        )
        self.configuration_button.clicked.connect(self.__configuration)

        # MINIMIZE BUTTON
        self.minimize_app_button = self.findChild(
            QtWidgets.QPushButton, "minimizeButton"
        )
        self.minimize_app_button.clicked.connect(lambda: self.showMinimized())

        # MAXIMIZE BUTTON
        self.maximize_restore_app_button = self.findChild(
            QtWidgets.QPushButton, "maximizeRestoreButton"
        )
        self.maximize_restore_app_button.clicked.connect(
            lambda: self.__maximize_restore_app()
        )

        # CLOSE BUTTON
        self.close_app_button = self.findChild(QtWidgets.QPushButton, "closeButton")
        self.close_app_button.clicked.connect(lambda: self.close())

        # PAGES
        self.pages = self.findChild(QtWidgets.QStackedWidget, "pages")

        self.navigation_buttons = self.findChild(QtWidgets.QFrame, "navigationButtons")

        # NEXT BUTTON
        self.next_button = self.findChild(QtWidgets.QPushButton, "nextButton")
        self.next_button.clicked.connect(lambda: self.__next_page())

        # BACK BUTTON
        self.back_button = self.findChild(QtWidgets.QPushButton, "backButton")
        self.back_button.clicked.connect(lambda: self.__back_page())
        self.back_button.hide()

        # SET VERSION
        self.version = self.findChild(QtWidgets.QLabel, "version")
        self.version.setText("v" + self.__get_version())

    def __configuration(self):
        ConfigurationView().exec()

    def __maximize_restore_app(self):
        icon = resolve_path("_ui/icons/icon_maximize.png")

        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            icon = resolve_path("_ui/icons/icon_restore.png")

        self.maximize_restore_app_button.setIcon(QtGui.QIcon(resolve_path(icon)))

    def __next_page(self):

        if self.pages.currentIndex() == 0:
            self.pages.setCurrentIndex(self.pages.currentIndex() + 1)
            self.back_button.show()

            if self.pages.currentIndex() == self.pages.count() - 1:
                self.next_button.setText("Start")

        elif self.pages.currentIndex() == self.pages.count() - 1:
            print("Start")

    def __back_page(self):
        if self.pages.currentIndex() > 0:
            self.pages.setCurrentIndex(self.pages.currentIndex() - 1)
            self.next_button.setText("Next >")

        if self.pages.currentIndex() == 0:
            self.back_button.hide()

    def __get_version(self):
        parser = ConfigParser()
        parser.read(resolve_path("assets/config.ini"))
        version = parser.get("fit_properties", "version")

        return version


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Wizard()
    MainWindow.show()
    sys.exit(app.exec())
