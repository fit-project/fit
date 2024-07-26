# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
import subprocess

from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog

from view.error import Error as ErrorView

from view.util import get_case_info

from controller.verify_pec.verify_pec import verifyPec as verifyPecController
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck

from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)


from common.constants.view import verify_pec, verify_pdf_timestamp
from common.utility import (
    get_platform,
    get_ntp_date_and_time,
    resolve_path,
    get_version,
)


class VerifyPec(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, wizard):
        super(VerifyPec, self).__init__(wizard)
        self.acquisition_directory = None
        self.wizard = wizard
        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/verify_pec/verify_pec.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # CUSTOM TOP BAR
        self.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.close_button.clicked.connect(self.close)

        # SET VERSION
        self.version.setText("v" + get_version())

        # EML FOLDER BUTTON
        self.eml_folder_button.clicked.connect(self.__select_eml_file)

        # VERIFICATION BUTTON
        self.verification_button.clicked.connect(self.__verify)
        self.verification_button.setEnabled(False)

        # DISABLE VERIFY BUTTON IF FIELD IS EMPTY
        self.eml_folder_input.textChanged.connect(self.__enable_verify_button)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def __enable_verify_button(self):
        self.verification_button.setEnabled(bool(self.eml_folder_input.text()))

    def __verify(self):

        ntp = get_ntp_date_and_time(
            NetworkControllerCheck().configuration["ntp_server"]
        )

        path = os.path.dirname(str(self.eml_folder_input.text()))

        try:
            pec = verifyPecController()
            pec.verify(self.eml_folder_input.text(), get_case_info(path), ntp)
            msg = QtWidgets.QMessageBox()
            msg.setWindowFlags(
                QtCore.Qt.WindowType.CustomizeWindowHint
                | QtCore.Qt.WindowType.WindowTitleHint
            )
            msg.setWindowTitle(verify_pdf_timestamp.VERIFICATION_COMPLETED)
            msg.setText(verify_pec.VERIFY_PEC_SUCCESS_MSG)
            msg.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No
            )
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            return_value = msg.exec()
            if return_value == QtWidgets.QMessageBox.StandardButton.Yes:

                platform = get_platform()
                if platform == "win":
                    os.startfile(
                        os.path.join(path, "report_integrity_pec_verification.pdf")
                    )
                elif platform == "osx":
                    subprocess.call(
                        [
                            "open",
                            os.path.join(path, "report_integrity_pec_verification.pdf"),
                        ]
                    )
                else:  # platform == 'lin' || platform == 'other'
                    subprocess.call(
                        [
                            "xdg-open",
                            os.path.join(path, "report_integrity_pec_verification.pdf"),
                        ]
                    )
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                verify_pec.VERIFY_PEC_FAIL,
                verify_pec.VERIFY_PEC_FAIL_MGS,
                str(e),
            )
            error_dlg.exec()

    def __select_eml_file(self):
        file, check = QFileDialog.getOpenFileName(
            None,
            verify_pec.OPEN_EML_FILE,
            os.path.expanduser(
                GeneralConfigurationController().configuration["cases_folder_path"]
            ),
            verify_pec.EML_FILES,
        )
        if check:
            self.eml_folder_input.setText(file)

    def __back_to_wizard(self):
        self.deleteLater()
        self.wizard.reload_case_info()
        self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
