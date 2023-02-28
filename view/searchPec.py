#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######
import datetime
import os

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator, QDoubleValidator
from PyQt5.QtWidgets import QVBoxLayout, QTreeWidget, QTreeWidgetItem, QAbstractItemView

from common.error import ErrorMessage
from view.configuration import Configuration as ConfigurationView
from view.case import Case as CaseView
from controller.searchPec import SearchPec as SearchPecController

class SearchPec(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

    def __init__(self, *args, **kwargs):
        super(SearchPec, self).__init__(*args, **kwargs)
        self.input_pec = None
        self.input_password = None
        self.input_server = None
        self.input_port = None
        self.input_sender = None
        self.input_recipient = None
        self.input_case = None
        self.input_from_date = None
        self.input_to_date = None
        self.error_msg = ErrorMessage()


    def init(self, case_info):
        self.width = 1140
        self.height = 590
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()
        self.setObjectName("search_pec_window")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")


        # PEC GROUP
        self.pec_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.pec_group_box.setEnabled(True)
        self.pec_group_box.setGeometry(QtCore.QRect(50, 20, 430, 200))
        self.pec_group_box.setObjectName("pec_group_box")

        # SCRAPED EMAILS TREE
        layout = QVBoxLayout()
        self.pec_tree = QTreeWidget(self.centralwidget)
        self.pec_tree.setGeometry(QtCore.QRect(510, 25, 590, 470))
        self.pec_tree.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.pec_tree.setObjectName("emails_tree")
        self.pec_tree.setSelectionMode(QAbstractItemView.SingleSelection)

        self.pec_tree.setHeaderLabel("Pec trovate")
        self.root = QTreeWidgetItem(["Inbox"])
        self.pec_tree.addTopLevelItem(self.root)
        layout.addWidget(self.pec_tree)

        # EMAIL FIELD
        self.input_pec = QtWidgets.QLineEdit(self.centralwidget)
        self.input_pec.setGeometry(QtCore.QRect(180, 60, 240, 20))
        self.input_pec.setText('example@pec-legal.it')
        pec_regex = QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")  # check
        validator = QRegExpValidator(pec_regex)
        self.input_pec.setValidator(validator)
        self.input_pec.setObjectName("input_pec")

        # PASSWORD FIELD
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(180, 95, 240, 20))
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.setText('password')
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # SERVER FIELD
        self.input_server = QtWidgets.QLineEdit(self.centralwidget)
        self.input_server.setGeometry(QtCore.QRect(180, 130, 240, 20))
        self.input_server.setText('imap.pec-email.com')
        self.input_server.setObjectName("input_server")

        # PORT FIELD
        self.input_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_port.setGeometry(QtCore.QRect(180, 165, 240, 20))
        self.input_port.setText('993')
        validator = QDoubleValidator()
        self.input_port.setValidator(validator)
        self.input_port.setObjectName("input_port")

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_pec, self.input_password, self.input_server, self.input_port]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

        # EMAIL LABEL
        self.label_pec = QtWidgets.QLabel(self.centralwidget)
        self.label_pec.setGeometry(QtCore.QRect(90, 60, 80, 20))
        self.label_pec.setAlignment(QtCore.Qt.AlignRight)
        self.label_pec.setObjectName("label_pec")

        # PASSWORD LABEL
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(90, 95, 80, 20))
        self.label_password.setAlignment(QtCore.Qt.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER LABEL
        self.label_server = QtWidgets.QLabel(self.centralwidget)
        self.label_server.setGeometry(QtCore.QRect(90, 130, 80, 20))
        self.label_server.setAlignment(QtCore.Qt.AlignRight)
        self.label_server.setObjectName("label_server")

        # PORT LABEL
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setGeometry(QtCore.QRect(90, 165, 80, 20))
        self.label_port.setAlignment(QtCore.Qt.AlignRight)
        self.label_port.setObjectName("label_port")

        # SCRAPING CRITERIA
        self.criteria_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.criteria_group_box.setEnabled(True)
        self.criteria_group_box.setGeometry(QtCore.QRect(50, 260, 430, 235))
        self.criteria_group_box.setObjectName("criteria_group_box")

        # SENDER FIELD
        self.input_sender = QtWidgets.QLineEdit(self.centralwidget)
        self.input_sender.setGeometry(QtCore.QRect(180, 300, 240, 20))
        self.input_sender.setObjectName("input_sender")

        # RECIPIENT FIELD
        self.input_recipient = QtWidgets.QLineEdit(self.centralwidget)
        self.input_recipient.setGeometry(QtCore.QRect(180, 335, 240, 20))
        self.input_recipient.setObjectName("input_recipient")

        # CASE FIELD
        self.input_case = QtWidgets.QLineEdit(self.centralwidget)
        self.input_case.setGeometry(QtCore.QRect(180, 370, 240, 20))
        self.input_case.setObjectName("input_case")

        # FROM DATE FIELD
        self.input_from_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_from_date.setGeometry(QtCore.QRect(180, 405, 240, 20))
        self.input_from_date.setDate(QDate(1990, 1, 1))
        self.input_from_date.setObjectName("input_from_date")

        # TO DATE FIELD
        self.input_to_date = QtWidgets.QDateEdit(self.centralwidget)
        self.input_to_date.setGeometry(QtCore.QRect(180, 440, 240, 20))
        self.input_to_date.setDate(QDate.currentDate())
        self.input_to_date.setObjectName("input_to_date")

        # SENDER LABEL
        self.label_sender = QtWidgets.QLabel(self.centralwidget)
        self.label_sender.setGeometry(QtCore.QRect(90, 300, 80, 20))
        self.label_sender.setAlignment(QtCore.Qt.AlignRight)
        self.label_sender.setObjectName("label_sender")


        # RECIPIENT LABEL
        self.label_recipient = QtWidgets.QLabel(self.centralwidget)
        self.label_recipient.setGeometry(QtCore.QRect(90, 335, 80, 20))
        self.label_recipient.setAlignment(QtCore.Qt.AlignRight)
        self.label_recipient.setObjectName("label_recipient")

        # CASE LABEL
        self.label_case = QtWidgets.QLabel(self.centralwidget)
        self.label_case.setGeometry(QtCore.QRect(90, 370, 80, 20))
        self.label_case.setAlignment(QtCore.Qt.AlignRight)
        self.label_case.setObjectName("label_case")

        # FROM DATE LABEL
        self.label_from_date = QtWidgets.QLabel(self.centralwidget)
        self.label_from_date.setGeometry(QtCore.QRect(90, 405, 80, 20))
        self.label_from_date.setAlignment(QtCore.Qt.AlignRight)
        self.label_from_date.setObjectName("label_from_date")

        # TO DATE LABEL
        self.label_to_date = QtWidgets.QLabel(self.centralwidget)
        self.label_to_date.setGeometry(QtCore.QRect(90, 440, 80, 20))
        self.label_to_date.setAlignment(QtCore.Qt.AlignRight)
        self.label_to_date.setObjectName("label_to_date")

        # LOGIN BUTTON
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setGeometry(QtCore.QRect(405, 505, 75, 25))
        self.login_button.clicked.connect(self.login)
        self.login_button.setObjectName("StartAcquisitionAction")
        self.login_button.setEnabled(True)

        # VERIFY BUTTON
        self.verify_button = QtWidgets.QPushButton(self.centralwidget)
        self.verify_button.setGeometry(QtCore.QRect(1025, 505, 75, 25))
        self.verify_button.clicked.connect(self.verify_eml)
        self.verify_button.setObjectName("StartAction")
        self.verify_button.setEnabled(False)

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menuConfiguration = QtWidgets.QAction("Configuration", self)
        self.menuConfiguration.setObjectName("menuConfiguration")
        self.menuConfiguration.triggered.connect(self.configuration)
        self.menuBar().addAction(self.menuConfiguration)

        # CASE BUTTON
        self.case_action = QtWidgets.QAction("Case", self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.case)
        self.menuBar().addAction(self.case_action)

        # ACQUISITION BUTTON
        self.acquisition_menu = self.menuBar().addMenu("&Acquisition")
        self.acquisition_status_action = QtWidgets.QAction(QtGui.QIcon(os.path.join('asset/images', 'info.png')),
                                                           "Status",
                                                           self)
        self.acquisition_status_action.triggered.connect(self._acquisition_status)
        self.acquisition_status_action.setObjectName("StatusAcquisitionAction")
        self.acquisition_menu.addAction(self.acquisition_status_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        # Get timestamp parameters
        self.configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")

        # Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')
        # Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))



    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("eml_verify_window", "Freezing Internet Tool"))
        self.pec_group_box.setTitle(_translate("eml_verify_window", "Impostazioni server PEC"))
        self.criteria_group_box.setTitle(_translate("eml_verify_window", "Criteri di ricerca"))
        self.label_pec.setText(_translate("eml_verify_window", "PEC*"))
        self.label_password.setText(_translate("eml_verify_window", "Password*"))
        self.label_server.setText(_translate("eml_verify_window", "Server PEC*"))
        self.label_port.setText(_translate("eml_verify_window", "Port*"))
        self.label_sender.setText(_translate("email_scrape_window", "Mittente"))
        self.label_recipient.setText(_translate("email_scrape_window", "Destinatario"))
        self.label_case.setText(_translate("eml_verify_window", "Caso"))
        self.label_from_date.setText(_translate("eml_verify_window", "Data di inizio"))
        self.label_to_date.setText(_translate("eml_verify_window", "Data di fine"))
        self.login_button.setText(_translate("eml_verify_window", "Fetch"))
        self.verify_button.setText(_translate("eml_verify_window", "Verify"))

    def login(self):
        self.pec_tree.clear()
        self.root = QTreeWidgetItem(["Inbox"])
        self.pec_tree.addTopLevelItem(self.root)


        searchPec = SearchPecController(self.input_pec.text(), self.input_password.text(), self.input_server.text(),
                                        self.input_port.text(), self.case_info)
        messages = searchPec.fetchPec()

        sender = self.input_sender.text()
        recipient = self.input_recipient.text()
        case = self.input_case.text()
        fromDate = datetime.datetime(self.input_from_date.date().year(), self.input_from_date.date().month(),
                                     self.input_from_date.date().day())
        fromDate = fromDate.date()
        toDate = datetime.datetime(self.input_to_date.date().year(), self.input_to_date.date().month(),
                                   self.input_to_date.date().day())
        toDate = toDate.date()

        #CONTROLLO MITTENTE
        filteredPecs = []
        if len(sender) == 0:
            pass
        else:
            for message in messages:
                senderPec = message.get_address('from')[0]
                list = senderPec.split()
                pecIndex = list.index("di:")
                senderPec = " ".join(list[pecIndex + 1:])
                if senderPec == sender:
                    filteredPecs.append(message)
            messages = filteredPecs

        #CONTROLLO DESTINATARIO
        filteredPecs = []
        if len(recipient) == 0:
            pass
        else:
            for message in messages:
                if message.get_address('to')[1] == recipient:
                    filteredPecs.append(message)
            messages = filteredPecs

        # CONTROLLO CASO
        filteredPecs = []
        if len(case) == 0:
            pass
        else:
            for message in messages:
                subject = message.get_subject()
                list = subject.split()
                caseIndex = list.index("caso:")
                casePec = " ".join(list[caseIndex + 1:])
                if casePec == case:
                    filteredPecs.append(message)
            messages = filteredPecs

        # CONTROLLO DATA FROM
        filteredPecs = []
        data = "1990-01-01"
        defaultData = datetime.datetime.strptime(data, '%Y-%m-%d')
        defaultData = defaultData.date()

        if fromDate == defaultData:
            pass
        else:
            for message in messages:
                datePec = message.get_decoded_header('Date')
                datePec = datetime.datetime.strptime(datePec, '%a, %d %b %Y %H:%M:%S %z')
                datePec = datePec.date()
                if datePec > fromDate or datePec == fromDate:
                    filteredPecs.append(message)
            messages = filteredPecs

        # CONTROLLO DATA TO
        filteredPecs = []
        dataToday = datetime.datetime.today()
        dataToday = dataToday.date()

        if toDate == dataToday:
            pass
        else:
            for message in messages:
                datePec = message.get_decoded_header('Date')
                datePec = datetime.datetime.strptime(datePec, '%a, %d %b %Y %H:%M:%S %z')
                datePec = datePec.date()
                if datePec < toDate or datePec == toDate:
                    filteredPecs.append(message)
            messages = filteredPecs

        for message in messages:
            subject = message.get_subject()
            date_str = str(message.get_decoded_header('Date'))
            sender = message.get_decoded_header('From')
            uid = message.get('Message-ID')
            dict_value = 'Mittente: ' + sender + '\nData: ' \
                         + date_str + '\nOggetto: ' + subject + '\nUID: ' + uid + '\n' + '\n'
            self.email_folder = QTreeWidgetItem([dict_value])
            self.root.addChild(self.email_folder)

        self.pec_tree.expandItem(self.root)
        self.verify_button.setEnabled(True)

    def _acquisition_status(self):
        self.acquisition_status.show()

    def verify_eml(self):

        searchPec = SearchPecController(self.input_pec.text(), self.input_password.text(), self.input_server.text(),
                                        self.input_port.text(), self.case_info)
        pecSelected = self.pec_tree.currentItem()
        uid = pecSelected.text(0)
        indiceUid = uid.find("UID:")
        uidSlice = uid[indiceUid + len("UID:") + 1:]

        pecs = searchPec.fetchPec()
        directory = os.path.join(os.path.expanduser(self.configuration_general.configuration['cases_folder_path']),
                                 self.case_info['name'], 'Eml files')
        searchPec.verifyEml(uidSlice, pecs, directory)

    def onTextChanged(self):
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


