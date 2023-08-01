#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import hashlib
import os
import subprocess

import rfc3161ng


from view.menu_bar import MenuBar as MenuBarView


from controller.verify_pdf_timestamp import (
    VerifyPDFTimestamp as VerifyPDFTimestampController,
)
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog

from common.utility import get_ntp_date_and_time, get_platform
from common.constants.view import verify_pdf_timestamp, general


class VerifyPDFTimestamp(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(VerifyPDFTimestamp, self).__init__(*args, **kwargs)

        self.data = None  # acquisition_report.pdf
        self.tsr_in = None  # timestamp.tsr
        self.untrusted = None  # tsa.crt

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.width = 690
        self.height = 250
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info

        self.acquisition_directory = None
        if options:
            if "acquisition_directory" in options:
                self.acquisition_directory = options["acquisition_directory"]

        self.setWindowIcon(QtGui.QIcon(os.path.join("assets/svg/", "FIT.svg")))
        self.setObjectName("verify_timestamp_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet(
            "QWidget {background-color: rgb(255, 255, 255);}"
        )
        self.setCentralWidget(self.centralwidget)

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        #### - START MENU BAR - #####
        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        # This bar is common on all main window
        self.menu_bar = MenuBarView(self, self.case_info)

        # Add default menu on menu bar
        self.menu_bar.add_default_actions()
        self.setMenuBar(self.menu_bar)
        #### - END MENUBAR - #####

        # TIMESTAMP GROUP
        self.timestamp_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.timestamp_group_box.setEnabled(True)
        self.timestamp_group_box.setGeometry(QtCore.QRect(50, 20, 590, 200))
        self.timestamp_group_box.setObjectName("timestamp_group_box")
        # PDF FIELD
        self.input_pdf = QtWidgets.QLineEdit(self.centralwidget)
        self.input_pdf.setGeometry(QtCore.QRect(215, 60, 300, 20))
        self.input_pdf.setFont(font)
        self.input_pdf.setObjectName("input_pdf")
        self.input_pdf.setEnabled(False)
        self.input_pdf_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_pdf_button.setGeometry(QtCore.QRect(515, 60, 75, 20))
        self.input_pdf_button.setFont(font)
        self.input_pdf_button.clicked.connect(lambda extension: self.dialog("pdf"))

        # TSR FIELD
        self.input_tsr = QtWidgets.QLineEdit(self.centralwidget)
        self.input_tsr.setGeometry(QtCore.QRect(215, 95, 300, 20))
        self.input_tsr.setFont(font)
        self.input_tsr.setObjectName("input_tsr")
        self.input_tsr.setEnabled(False)
        self.input_tsr_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_tsr_button.setGeometry(QtCore.QRect(515, 95, 75, 20))
        self.input_tsr_button.setFont(font)
        self.input_tsr_button.clicked.connect(lambda extension: self.dialog("tsr"))

        # CRT FIELD
        self.input_crt = QtWidgets.QLineEdit(self.centralwidget)
        self.input_crt.setGeometry(QtCore.QRect(215, 130, 300, 20))
        self.input_crt.setFont(font)
        self.input_crt.setObjectName("input_crt")
        self.input_crt.setEnabled(False)
        self.input_crt_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_crt_button.setGeometry(QtCore.QRect(515, 130, 75, 20))
        self.input_crt_button.setFont(font)
        self.input_crt_button.clicked.connect(lambda extension: self.dialog("crt"))

        # PDF LABEL
        self.label_pdf = QtWidgets.QLabel(self.centralwidget)
        self.label_pdf.setGeometry(QtCore.QRect(90, 60, 120, 20))
        self.label_pdf.setFont(font)
        self.label_pdf.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_pdf.setObjectName("label_pdf")

        # TSR LABEL
        self.label_tsr = QtWidgets.QLabel(self.centralwidget)
        self.label_tsr.setGeometry(QtCore.QRect(90, 95, 120, 20))
        self.label_tsr.setFont(font)
        self.label_tsr.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_tsr.setObjectName("label_tsr")

        # CRT LABEL
        self.label_crt = QtWidgets.QLabel(self.centralwidget)
        self.label_crt.setGeometry(QtCore.QRect(90, 130, 120, 20))
        self.label_crt.setFont(font)
        self.label_crt.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_crt.setObjectName("label_crt")

        # VERIFICATION BUTTON
        self.verification_button = QtWidgets.QPushButton(self)
        self.verification_button.setGeometry(QtCore.QRect(300, 190, 75, 30))
        self.verification_button.clicked.connect(self.verify)
        self.verification_button.setFont(font)
        self.verification_button.setObjectName("StartAction")
        self.verification_button.setEnabled(False)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_pdf, self.input_tsr, self.input_crt]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.timestamp_group_box.setTitle(verify_pdf_timestamp.TIMESTAMP_SETTINGS)
        self.label_pdf.setText(verify_pdf_timestamp.PDF_LABEL)
        self.label_tsr.setText(verify_pdf_timestamp.TSR_LABEL)
        self.label_crt.setText(verify_pdf_timestamp.CRT_LABEL)
        self.verification_button.setText(general.BUTTON_VERIFY)
        self.input_pdf_button.setText(general.BROWSE)
        self.input_tsr_button.setText(general.BROWSE)
        self.input_crt_button.setText(general.BROWSE)

    def verify(self):
        tsr_in = self.input_tsr.text()
        untrusted = self.input_crt.text()
        data = self.input_pdf.text()

        certificate = open(untrusted, "rb").read()
        configuration_timestamp = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_timestamp"
        )
        options = configuration_timestamp.options
        server_name = options["server_name"]

        # verify timestamp
        rt = rfc3161ng.RemoteTimestamper(
            server_name, certificate=certificate, hashname="sha256"
        )
        timestamp = open(tsr_in, "rb").read()

        try:
            verified = rt.check(timestamp, data=open(data, "rb").read())

            report, info_file_path = self.generate_report_verification(
                data, server_name, timestamp, True
            )
            if verified:
                report.generate_pdf(True, info_file_path)

                msg = QtWidgets.QMessageBox()
                msg.setWindowFlags(
                    QtCore.Qt.WindowType.CustomizeWindowHint
                    | QtCore.Qt.WindowType.WindowTitleHint
                )
                msg.setWindowTitle(verify_pdf_timestamp.VERIFICATION_COMPLETED)
                msg.setText(verify_pdf_timestamp.VERIFICATION_SUCCESS)
                msg.setInformativeText(verify_pdf_timestamp.VALID_TIMESTAMP_REPORT)
                msg.setStandardButtons(
                    QtWidgets.QMessageBox.StandardButton.Yes
                    | QtWidgets.QMessageBox.StandardButton.No
                )
                msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
                return_value = msg.exec()
                if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
                    path = self.get_current_dir()
                    platform = get_platform()
                    if platform == "win":
                        os.startfile(
                            os.path.join(path, "report_timestamp_verification.pdf")
                        )
                    elif platform == "osx":
                        subprocess.call(
                            [
                                "open",
                                os.path.join(path, "report_timestamp_verification.pdf"),
                            ]
                        )
                    else:  # platform == 'lin' || platform == 'other'
                        subprocess.call(
                            [
                                "xdg-open",
                                os.path.join(path, "report_timestamp_verification.pdf"),
                            ]
                        )

        except Exception:
            # timestamp not validated

            report, info_file_path = self.generate_report_verification(
                data, server_name, timestamp, False
            )
            report.generate_pdf(False, info_file_path)

            msg = QtWidgets.QMessageBox()
            msg.setWindowFlags(
                QtCore.Qt.WindowType.CustomizeWindowHint
                | QtCore.Qt.WindowType.WindowTitleHint
            )
            msg.setWindowTitle(verify_pdf_timestamp.VERIFICATION_COMPLETED)
            msg.setText(verify_pdf_timestamp.VERIFICATION_FAIL)
            msg.setInformativeText(verify_pdf_timestamp.INVALID_TIMESTAMP_REPORT)
            msg.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No
            )
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            return_value = msg.exec()
            if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
                path = self.get_current_dir()
                platform = get_platform()
                if platform == "win":
                    os.startfile(
                        os.path.join(path, "report_timestamp_verification.pdf")
                    )
                elif platform == "osx":
                    subprocess.call(
                        [
                            "open",
                            os.path.join(path, "report_timestamp_verification.pdf"),
                        ]
                    )
                else:  # platform == 'lin' || platform == 'other'
                    subprocess.call(
                        [
                            "xdg-open",
                            os.path.join(path, "report_timestamp_verification.pdf"),
                        ]
                    )

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.verification_button.setEnabled(all_fields_filled)

    def dialog(self, extension):
        # open the correct file picker based on extension
        open_folder = self.get_current_dir()

        if extension == "pdf":
            file, check = QFileDialog.getOpenFileName(
                None,
                verify_pdf_timestamp.OPEN_PDF_FILE,
                open_folder,
                verify_pdf_timestamp.PDF_FILE,
            )
            if check:
                self.input_pdf.setText(file)
                self.acquisition_directory = os.path.dirname(file)
        elif extension == "tsr":
            file, check = QFileDialog.getOpenFileName(
                None,
                verify_pdf_timestamp.OPEN_TSR_FILE,
                open_folder,
                verify_pdf_timestamp.TSR_FILE,
            )
            if check:
                self.input_tsr.setText(file)

        elif extension == "crt":
            file, check = QFileDialog.getOpenFileName(
                None,
                verify_pdf_timestamp.OPEN_CRT_FILE,
                open_folder,
                verify_pdf_timestamp.CRT_FILE,
            )
            if check:
                self.input_crt.setText(file)

    def generate_report_verification(self, data, server_name, timestamp, check):
        ntp = get_ntp_date_and_time(
            NetworkControllerCheck().configuration["ntp_server"]
        )

        if check:
            verification = verify_pdf_timestamp.VALID_TIMESTAMP
        else:
            verification = verify_pdf_timestamp.INVALID_TIMESTAMP

        # calculate hash (as in rfc lib)
        hashobj = hashlib.new("sha256")
        hashobj.update(open(data, "rb").read())
        digest = hashobj.hexdigest()

        # get date from tsr file
        timestamp_datetime = rfc3161ng.get_timestamp(timestamp)

        info_file_path = os.path.join(self.acquisition_directory, "timestamp_info.txt")
        with open(info_file_path, "w") as file:
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_RESULT}\n")
            file.write(f"{verification}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_FILENAME}\n")
            file.write(f"{os.path.basename(self.input_pdf.text())}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_SIZE}\n")
            file.write(f"{os.path.getsize(self.input_pdf.text())} bytes\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_HASH_ALGORITHM}\n")
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_SHA256}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_DIGEST}\n")
            file.write(f"{digest}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_TIMESTAMP}\n")
            file.write(f"{str(timestamp_datetime)}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{verify_pdf_timestamp.REPORT_LABEL_SERVER}\n")
            file.write(f"{server_name}\n")
            file.write(
                "======================================================================\n"
            )

        report = VerifyPDFTimestampController(
            self.acquisition_directory, self.case_info, ntp
        )
        return report, info_file_path

    def get_current_dir(self):
        if not self.acquisition_directory:
            configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
                "configuration_general"
            )
            open_folder = os.path.expanduser(
                os.path.join(
                    configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                )
            )
            return open_folder
        else:
            return self.acquisition_directory

    def __back_to_wizard(self):
        self.deleteLater()
        self.wizard.reload_case_info()
        self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
