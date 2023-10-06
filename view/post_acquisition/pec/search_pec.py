#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import datetime
import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import (
    QRegularExpression,
    QDate,
    QRect,
    Qt,
    QEventLoop,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QRegularExpressionValidator, QDoubleValidator
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QDateEdit,
    QPushButton,
    QAbstractItemView,
    QDialog,
    QWidget,
    QGroupBox,
    QLineEdit,
    QLabel,
    QMessageBox,
)

from view.error import Error as ErrorView

from controller.search_pec import SearchPec as SearchPecController
from controller.pec import Pec as PecController

from controller.configurations.tabs.pec.pec import Pec as PecConfigController

from common.constants.view.pec import pec, search_pec
from common.constants.status import *
from view.spinner import Spinner


class SearchPec(QDialog):
    downloadedeml = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(SearchPec, self).__init__(*args, **kwargs)
        self.input_pec_email = None
        self.input_password = None
        self.input_imap_server = None
        self.input_imap_port = None
        self.input_to = None
        self.input_case = None
        self.input_from_date = None
        self.input_to_date = None
        self.controller = PecConfigController()
        self.downloaded_status = FAIL
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.spinner = Spinner()

    def init(self, case_info, acquisition_directory):
        self.width = 1140
        self.height = 590
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.acquisition_directory = acquisition_directory
        self.setObjectName("search_pec_window")
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet(
            "QWidget {background-color: rgb(255, 255, 255);}"
        )

        self.setWindowTitle("Freezing Internet Tool")
        self.setWindowIcon(QtGui.QIcon(os.path.join("assets/svg/", "FIT.svg")))

        # PEC GROUP
        self.pec_group_box = QGroupBox(self.centralwidget)
        self.pec_group_box.setEnabled(True)
        self.pec_group_box.setGeometry(QRect(50, 20, 430, 200))
        self.pec_group_box.setObjectName("pec_group_box")

        # SCRAPED EMAILS TREE
        layout = QVBoxLayout()
        self.pec_tree = QTreeWidget(self.centralwidget)
        self.pec_tree.setGeometry(QRect(510, 25, 590, 470))
        self.pec_tree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.pec_tree.setObjectName("emails_tree")
        self.pec_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.pec_tree.setHeaderLabel("Pec found")
        self.root = QTreeWidgetItem(["Inbox"])
        self.pec_tree.addTopLevelItem(self.root)
        layout.addWidget(self.pec_tree)

        # EMAIL FIELD
        self.input_pec_email = QLineEdit(self.centralwidget)
        self.input_pec_email.setGeometry(QRect(180, 60, 240, 20))
        self.input_pec_email.setText("example@pec-legal.it")
        pec_regex = QRegularExpression("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")  # check
        validator = QRegularExpressionValidator(pec_regex)
        self.input_pec_email.setValidator(validator)
        self.input_pec_email.setObjectName("input_pec_email")

        # PASSWORD FIELD
        self.input_password = QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QRect(180, 95, 240, 20))
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setText("password")
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # SERVER FIELD
        self.input_imap_server = QLineEdit(self.centralwidget)
        self.input_imap_server.setGeometry(QRect(180, 130, 240, 20))
        self.input_imap_server.setText("imap.pec-email.com")
        self.input_imap_server.setObjectName("input_server")

        # PORT FIELD
        self.input_imap_port = QLineEdit(self.centralwidget)
        self.input_imap_port.setGeometry(QRect(180, 165, 240, 20))
        self.input_imap_port.setText("993")
        validator = QDoubleValidator()
        self.input_imap_port.setValidator(validator)
        self.input_imap_port.setObjectName("input_port")

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [
            self.input_pec_email,
            self.input_password,
            self.input_imap_server,
            self.input_imap_port,
        ]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        # EMAIL LABEL
        self.label_pec_email = QLabel(self.centralwidget)
        self.label_pec_email.setGeometry(QRect(90, 60, 80, 20))
        self.label_pec_email.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_pec_email.setObjectName("label_pec")

        # PASSWORD LABEL
        self.label_password = QLabel(self.centralwidget)
        self.label_password.setGeometry(QRect(90, 95, 80, 20))
        self.label_password.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER LABEL
        self.label_imap_server = QLabel(self.centralwidget)
        self.label_imap_server.setGeometry(QRect(90, 130, 80, 20))
        self.label_imap_server.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_imap_server.setObjectName("label_server")

        # PORT LABEL
        self.label_imap_port = QLabel(self.centralwidget)
        self.label_imap_port.setGeometry(QRect(90, 165, 80, 20))
        self.label_imap_port.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_imap_port.setObjectName("label_port")

        # SCRAPING CRITERIA
        self.criteria_group_box = QGroupBox(self.centralwidget)
        self.criteria_group_box.setEnabled(True)
        self.criteria_group_box.setGeometry(QRect(50, 260, 430, 235))
        self.criteria_group_box.setObjectName("criteria_group_box")

        # RECIPIENT FIELD
        self.input_to = QLineEdit(self.centralwidget)
        self.input_to.setGeometry(QRect(180, 335, 240, 20))
        self.input_to.setPlaceholderText(search_pec.PLACEHOLDER_TO)
        self.input_to.setObjectName("input_recipient")

        # CASE FIELD
        self.input_case = QLineEdit(self.centralwidget)
        self.input_case.setGeometry(QRect(180, 370, 240, 20))
        self.input_to.setPlaceholderText(search_pec.PLACEHOLDER_SUBJECT)
        self.input_case.setObjectName("input_case")

        # FROM DATE FIELD
        self.input_from_date = QDateEdit(self.centralwidget)
        self.input_from_date.setGeometry(QRect(180, 405, 240, 20))
        self.input_from_date.setDate(QDate.currentDate().addDays(-14))
        self.input_from_date.setObjectName("input_from_date")

        # TO DATE FIELD
        self.input_to_date = QDateEdit(self.centralwidget)
        self.input_to_date.setGeometry(QRect(180, 440, 240, 20))
        self.input_to_date.setDate(QDate.currentDate())
        self.input_to_date.setObjectName("input_to_date")

        # TO LABEL
        self.label_to = QLabel(self.centralwidget)
        self.label_to.setGeometry(QRect(90, 335, 80, 20))
        self.label_to.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_to.setObjectName("label_recipient")

        # CASE LABEL
        self.label_case = QLabel(self.centralwidget)
        self.label_case.setGeometry(QRect(90, 370, 80, 20))
        self.label_case.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_case.setObjectName("label_case")

        # FROM DATE LABEL
        self.label_from_date = QLabel(self.centralwidget)
        self.label_from_date.setGeometry(QRect(90, 405, 80, 20))
        self.label_from_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_from_date.setObjectName("label_from_date")

        # TO DATE LABEL
        self.label_to_date = QLabel(self.centralwidget)
        self.label_to_date.setGeometry(QRect(90, 440, 80, 20))
        self.label_to_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_to_date.setObjectName("label_to_date")

        # LOGIN BUTTON
        self.login_button = QPushButton(self.centralwidget)
        self.login_button.setGeometry(QRect(405, 505, 75, 25))
        self.login_button.clicked.connect(self.login)
        self.login_button.setObjectName("StartAcquisitionAction")
        self.login_button.setEnabled(True)

        # VERIFY BUTTON
        self.download_button = QPushButton(self.centralwidget)
        self.download_button.setGeometry(QRect(1025, 505, 75, 25))
        self.download_button.clicked.connect(self.__download_eml)
        self.download_button.setObjectName("StartAction")
        self.download_button.setEnabled(False)

        self.options = self.controller.options
        if self.options:
            self.input_pec_email.setText(self.options.get("pec_email"))
            self.input_password.setText(self.options.get("password"))
            self.input_imap_server.setText(self.options.get("imap_server"))
            self.input_imap_port.setText(self.options.get("imap_port"))

        self.retranslateUi()

    def retranslateUi(self):
        self.pec_group_box.setTitle(search_pec.SETTINGS)
        self.criteria_group_box.setTitle(search_pec.CRITERIA)
        self.label_pec_email.setText(search_pec.LABEL_USERNAME)
        self.label_password.setText(search_pec.LABEL_PASSWORD)
        self.label_imap_server.setText(search_pec.LABEL_IMAP_SERVER)
        self.label_imap_port.setText(search_pec.LABEL_IMAP_PORT)
        self.label_to.setText(search_pec.LABEL_TO)
        self.label_case.setText(search_pec.LABEL_CASE)
        self.label_from_date.setText(search_pec.LABEL_FROM_DATE)
        self.label_to_date.setText(search_pec.LABEL_TO_DATE)
        self.login_button.setText(search_pec.LOGIN_BUTTON)
        self.download_button.setText(search_pec.DOWNLOAD_BUTTON)

    def login(self):
        self.centralwidget.setEnabled(False)

        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()

        self.pec_tree.clear()
        self.root = QTreeWidgetItem(["Inbox"])
        self.pec_tree.addTopLevelItem(self.root)

        search_pec = SearchPecController(
            self.input_pec_email.text(),
            self.input_password.text(),
            self.input_imap_server.text(),
            self.input_imap_port.text(),
            self.case_info,
        )

        to = self.input_to.text()
        case = self.input_case.text()
        from_date = datetime.datetime(
            self.input_from_date.date().year(),
            self.input_from_date.date().month(),
            self.input_from_date.date().day(),
        )
        from_date = from_date.date()
        to_date = datetime.datetime(
            self.input_to_date.date().year(),
            self.input_to_date.date().month(),
            self.input_to_date.date().day(),
        )
        to_date = to_date.date()

        search_criteria = f'SUBJECT "POSTA CERTIFICATA:"'

        # CHECK TO
        if len(to) > 0:
            search_criteria = search_criteria + f' TO "{to}"'

        # CHECK CASE
        if len(case) > 0:
            search_criteria = search_criteria + f' SUBJECT "{case}"'

        # CHECK FROM DATE
        data = "1990-01-01"
        default_data = datetime.datetime.strptime(data, "%Y-%m-%d")
        default_data = default_data.date()

        if from_date != default_data:
            from_date = from_date.strftime("%d-%b-%Y")
            search_criteria = search_criteria + f' SINCE "{from_date}"'

        # CHECK DATE TO
        data_today = datetime.datetime.today()
        data_today = data_today.date()

        if to_date != data_today:
            to_date = to_date.strftime("%d-%b-%Y")
            search_criteria = search_criteria + f' BEFORE "{to_date}"'

        messages = []
        try:
            messages = search_pec.fetch_pec(search_criteria)
        except Exception as e:
            error_dlg = ErrorView(
                QMessageBox.Icon.Critical, pec.LOGIN_FAILED, pec.IMAP_FAILED_MGS, str(e)
            )
            error_dlg.exec()

        for message in messages:
            subject = message.get_subject()
            date_str = str(message.get_decoded_header("Date"))
            sender = message.get_decoded_header("From")
            uid = message.get("Message-ID")
            dict_value = (
                "Mittente: "
                + sender
                + "\nData: "
                + date_str
                + "\nOggetto: "
                + subject
                + "\nUID: "
                + uid
                + "\n"
                + "\n"
            )
            self.email_folder = QTreeWidgetItem([dict_value])
            self.root.addChild(self.email_folder)

        self.spinner.stop()

        self.pec_tree.expandItem(self.root)
        self.download_button.setEnabled(True)

        self.centralwidget.setEnabled(True)

    def __download_eml(self):
        self.centralwidget.setEnabled(False)

        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()

        status = SUCCESS

        pec_selected = self.pec_tree.currentItem()
        uid = pec_selected.text(0)

        timestamp_index = uid.find("ID:")
        uid_index = uid.find("UID:")
        timestamp_slice = uid[timestamp_index + len("ID:") + 1 : uid_index]

        acquisition_index = uid.find("Acquisition Report")
        case_index = uid.find("case: ")
        acquisition_slice = uid[
            acquisition_index + len("Acquisition Report") + 1 : case_index
        ]
        case_slice = uid[case_index + len("case:") + 1 : timestamp_index]

        acquisition_slice = acquisition_slice.strip()
        timestamp_slice = timestamp_slice.strip()
        case_slice = case_slice.strip()

        pec_controller = PecController(
            self.input_pec_email.text(),
            self.input_password.text(),
            acquisition_slice,
            case_slice,
            self.acquisition_directory,
            None,
            None,
            self.input_imap_server.text(),
            self.input_imap_port.text(),
        )

        try:
            if pec_controller.retrieve_eml_from_timestamp(timestamp_slice):
                self.downloaded_status = SUCCESS
        except Exception as e:
            error_dlg = ErrorView(
                QMessageBox.Icon.Critical, pec.LOGIN_FAILED, pec.IMAP_FAILED_MGS, str(e)
            )
            error_dlg.exec()
        self.spinner.stop()
        self.centralwidget.setEnabled(True)

        self.close()

    def __on_text_changed(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_fields_filled)

    def on_item_selection_changed(self):
        selected_items = self.pec_tree.selectedItems()
        for item in selected_items:
            self.update_child_items(item, item.isSelected())

    def update_child_items(self, item, selected):
        child_count = item.childCount()
        for i in range(child_count):
            child_item = item.child(i)
            child_item.setSelected(selected)
            self.update_child_items(child_item, selected)

    def closeEvent(self, event):
        self.downloadedeml.emit(self.downloaded_status)
