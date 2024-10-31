# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os

from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog

from view.util import (
    get_case_info,
    show_finish_verification_dialog,
    get_verification_label_text,
    add_label_in_verification_status_list,
    VerificationTypes,
)

from controller.verify_pec.verify_pec import verifyPec as verifyPecController
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck

from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)

from common.constants.view import verify_pec
from common.constants.view.tasks import status
from common.utility import (
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
        self.verify_pec_controller = verifyPecController()
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
        self.version.setText(get_version())

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

    def __select_eml_file(self):
        file, check = QFileDialog.getOpenFileName(
            None,
            verify_pec.OPEN_EML_FILE,
            os.path.expanduser(
                GeneralConfigurationController().configuration.get("cases_folder_path")
            ),
            verify_pec.EML_FILES,
        )
        if check:
            self.eml_folder_input.setText(file)

    def __verify(self):

        self.verification_status_list.clear()
        signature = {}
        is_revoked = False
        is_integrity = False
        provider_name = ""
        is_on_agid_list = False

        verification_status, email_info = self.__check_expirationdate()

        if verification_status == status.SUCCESS:
            if len(email_info) > 0:
                signature = self.__check_signature_exist()
                is_revoked = self.__check_revoked()
                is_integrity = True
                provider_name, is_on_agid_list = self.__check_autority()

            else:
                label = "INFO: {}".format(
                    verify_pec.NO_MAIL_INFO_FOUD_AFTER_CHECK_EXPIRATIONDATE
                )
                add_label_in_verification_status_list(
                    self.verification_status_list, label
                )
                email_info = self.__get_mail_info_from_eml()
                signature = self.__check_signature_exist()

            eml_file_path = self.eml_folder_input.text()
            path = os.path.dirname(str(eml_file_path))
            ntp = get_ntp_date_and_time(
                NetworkControllerCheck().configuration["ntp_server"]
            )
            case_info = get_case_info(path)

            report_info = {
                "case_info": case_info,
                "ntp": ntp,
                "eml_file_path": eml_file_path,
                "is_integrity": is_integrity,
                "is_revoked": is_revoked,
                "provider_name": provider_name,
                "is_on_agid_list": is_on_agid_list,
            }
            report_info.update(email_info)
            report_info.update(signature)

            if self.__generate_report(report_info) == status.SUCCESS:
                show_finish_verification_dialog(path, VerificationTypes.PEC)
        else:
            label = "INFO: {}".format(verify_pec.CHECK_EXPIRATIONDATE_FAIL)
            add_label_in_verification_status_list(self.verification_status_list, label)

    def __check_expirationdate(self):

        email_info = dict()
        verification_status = status.SUCCESS
        verification_name = verify_pec.CHECK_EXPIRATIONDATE
        verification_message = ""

        try:
            email_info = self.verify_pec_controller.check_expirationdate(
                self.eml_folder_input.text()
            )
        except Exception as e:
            verification_status = status.FAIL
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.verification_status_list, label)

        return verification_status, email_info

    def __check_signature_exist(self):

        signature = {}
        verification_status = status.SUCCESS
        verification_name = verify_pec.CHECK_SIGNATURE
        verification_message = ""
        try:
            signature = self.verify_pec_controller.check_signature_exist(
                self.eml_folder_input.text()
            )
        except Exception as e:
            verification_status = status.FAIL
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.verification_status_list, label)

        return signature

    def __check_revoked(self):

        is_revoked = False
        verification_status = status.SUCCESS
        verification_name = verify_pec.CHECK_REVOKED
        verification_message = ""
        try:
            is_revoked = self.verify_pec_controller.check_revoked()
        except Exception as e:
            verification_status = status.FAIL
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.verification_status_list, label)

        return is_revoked

    def __check_autority(self):

        provider_name = ""
        is_on_agid_list = False

        verification_status = status.SUCCESS
        verification_name = verify_pec.CHECK_AUTORITY
        verification_message = ""
        try:
            provider_name, is_on_agid_list = self.verify_pec_controller.check_autority()
        except Exception as e:
            verification_status = status.FAIL
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.verification_status_list, label)

        return provider_name, is_on_agid_list

    def __get_mail_info_from_eml(self):
        email_info = {}
        verification_status = status.SUCCESS
        verification_name = verify_pec.GET_MAIL_INFO_FROM_EML
        verification_message = ""
        try:
            email_info = self.verify_pec_controller.get_mail_info_from_eml(
                self.eml_folder_input.text()
            )
        except Exception as e:
            verification_status = status.FAIL
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.verification_status_list, label)

        return email_info

    def __generate_report(self, report_info):

        verification_status = status.SUCCESS
        verification_name = verify_pec.GENARATE_REPORT
        verification_message = ""
        try:
            self.verify_pec_controller.ganerate_report(report_info)
        except Exception as e:
            verification_status = status.FAIL
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.verification_status_list, label)

        return verification_status

    def __back_to_wizard(self):
        self.deleteLater()
        self.wizard.reload_case_info()
        self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
