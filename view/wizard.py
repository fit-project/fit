#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os

from configparser import SafeConfigParser

from PyQt5 import QtCore, QtGui, QtWidgets

from common.constants import error
from common.constants.view import wizard, general
from view.configuration import Configuration as ConfigurationView
from view.case_form import CaseForm as CaseFormView
from view.error import Error as ErrorView

from common.constants.view.wizard import *
class CaseInfoPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(CaseInfoPage, self).__init__(parent)
        self.setObjectName("CaseInfoPage")
   
        self.case_info = {}

        self.configuration_view = ConfigurationView(self)

        self.case_form_widget = QtWidgets.QWidget(self)
        self.case_form_widget.setGeometry(QtCore.QRect(0, 0, 795, 515))
        self.case_form_widget.setObjectName("case_form_widget")

        self.form = CaseFormView(self.case_form_widget)
        self.form.setGeometry(QtCore.QRect(0, 0, 400, 200))
      

        x = (self.case_form_widget.frameGeometry().width()/2) - (self.form.frameGeometry().width()/2) -20
        y = (self.case_form_widget.frameGeometry().height()/2) - (self.form.frameGeometry().height()/2)
        self.form.move(x, y)
        
        self.configuration_button = QtWidgets.QPushButton(self)
        self.configuration_button.setGeometry(QtCore.QRect(400, 350, 100, 25))
        self.configuration_button.setObjectName("skip_button")
        self.configuration_button.setText("Configuration")
        self.configuration_button.clicked.connect(self.__configuration)

        #This allow to edit every row on combox
        self.form.name.setEditable(True)
        self.form.name.setCurrentIndex(-1)
        self.form.name.currentTextChanged.connect(self.completeChanged)
        self.form.case_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.form.name)
           
    def isComplete(self):
        if self.form.name.findText(self.form.name.currentText()) >= 0:
            self.set_case_information(self.form.name.currentText())
        else:
            self.clear_case_information()
        return self.form.name.currentText() != ""
    
    def set_case_information(self, name):
        self.case_info = next((item for item in self.form.cases if item["name"] == name), None)
        if self.case_info is not None:
            for keyword, value in self.case_info.items():
                item = self.findChild(QtCore.QObject, keyword)
                if item is not None:
                    if isinstance(item, QtWidgets.QLineEdit) is not False:
                        if value is not None:
                            item.setText(str(value))
                    if isinstance(item, QtWidgets.QComboBox):
                        if keyword in 'proceeding_type': 
                            if value is not None:
                                type_proceeding = next((proceeding for proceeding in self.form.proceedings if proceeding["id"] == value), None)
                                value = type_proceeding["name"]
                            
                            item.setCurrentText(value)
    
    def clear_case_information(self):
        self.case_info = {}
        self.form.lawyer_name.setText("")
        self.form.types_proceedings.setCurrentIndex(-1)
        self.form.courthouse.setText("")
        self.form.proceeding_number.setText("")
    
    def __configuration(self):
        self.configuration_view.exec_()
    


class SelectTaskPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(SelectTaskPage, self).__init__(parent)

        self.setObjectName("SelectTask")

        # Create a button group for radio buttons
        self.radio_button_group = QtWidgets.QButtonGroup()
        self.radio_button_group.buttonToggled[QtWidgets.QAbstractButton, bool].connect(self.completeChanged)
        self.radio_button_container = QtWidgets.QWidget(self)
        self.radio_button_container.setGeometry(QtCore.QRect(80, 80, 650, 112))
        self.radio_button_container.setObjectName("radio_button_container")
        self.radio_buttons_hlayout = QtWidgets.QHBoxLayout(self.radio_button_container)
        self.radio_buttons_hlayout.setContentsMargins(0, 0, 0, 0)
        self.radio_buttons_hlayout.setObjectName("radio_buttons_hlayout")

        
        #RADIO BUTTON WEB
        self.web_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.web_radio_button_wrapper.setStyleSheet("QWidget#web_radio_button_wrapper {\n""border: 1px solid black;\n""}")
        self.web_radio_button_wrapper.setObjectName("web_radio_button_wrapper")
        self.web_vlayout = QtWidgets.QVBoxLayout(self.web_radio_button_wrapper)
        self.web_vlayout.setContentsMargins(5, 5, 5, 5)
        self.web_vlayout.setObjectName("web_vlayout")
        self.web_img = QtWidgets.QLabel(self.web_radio_button_wrapper)
        self.web_img.setStyleSheet("image: url(assets/images/wizard/web.png);")
        self.web_img.setText("")
        self.web_img.setObjectName("web_img")
        self.web_vlayout.addWidget(self.web_img)
        self.web = QtWidgets.QRadioButton(self.web_radio_button_wrapper)
        self.web.setObjectName("web")
        self.web_vlayout.addWidget(self.web)
        self.radio_buttons_hlayout.addWidget(self.web_radio_button_wrapper)
        self.radio_button_group.addButton(self.web, 0)

        #RADIO BUTTON MAIL
        self.mail_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.mail_radio_button_wrapper.setStyleSheet("QWidget#mail_radio_button_wrapper {\n""border: 1px solid black;\n""}")
        self.mail_radio_button_wrapper.setObjectName("mail_radio_button_wrapper")
        self.mail_vlayout = QtWidgets.QVBoxLayout(self.mail_radio_button_wrapper)
        self.mail_vlayout.setContentsMargins(5, 5, 5, 5)
        self.mail_vlayout.setObjectName("mail_vlayout")
        self.mail_img = QtWidgets.QLabel(self.mail_radio_button_wrapper)
        self.mail_img.setEnabled(True)
        self.mail_img.setStyleSheet("image: url(assets/images/wizard/mail.png);\n")
        self.mail_img.setText("")
        self.mail_img.setObjectName("mail_img")
        self.mail_vlayout.addWidget(self.mail_img)
        self.mail = QtWidgets.QRadioButton(self.mail_radio_button_wrapper)
        self.mail.setEnabled(True)
        self.mail.setObjectName("mail")
        self.mail_vlayout.addWidget(self.mail)
        self.radio_buttons_hlayout.addWidget(self.mail_radio_button_wrapper)
        self.radio_button_group.addButton(self.mail, 1)

        # RADIO BUTTON INSTAGRAM
        self.insta_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.insta_radio_button_wrapper.setStyleSheet("QWidget#insta_radio_button_wrapper {\n""border: 1px solid black;\n""}")
        self.insta_radio_button_wrapper.setObjectName("insta_radio_button_wrapper")
        self.insta_vlayout = QtWidgets.QVBoxLayout(self.insta_radio_button_wrapper)
        self.insta_vlayout.setContentsMargins(5, 5, 5, 5)
        self.insta_vlayout.setObjectName("insta_vlayout")
        self.insta_img = QtWidgets.QLabel(self.insta_radio_button_wrapper)
        self.insta_img.setEnabled(True)
        self.insta_img.setStyleSheet("image: url(assets/images/wizard/instagram.png);")
        self.insta_img.setText("")
        self.insta_img.setObjectName("insta_img")
        self.insta_vlayout.addWidget(self.insta_img)
        self.insta = QtWidgets.QRadioButton(self.insta_radio_button_wrapper)
        self.insta.setEnabled(True)
        self.insta.setObjectName("insta")
        self.insta_vlayout.addWidget(self.insta)
        self.radio_buttons_hlayout.addWidget(self.insta_radio_button_wrapper)
        self.radio_button_group.addButton(self.insta, 3)

        # RADIO BUTTON VERIFY TIMESTAMP
        self.timestamp_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.timestamp_radio_button_wrapper.setStyleSheet("QWidget#timestamp_radio_button_wrapper {\n""border: 1px solid black;\n""}")
        self.timestamp_radio_button_wrapper.setObjectName("timestamp_radio_button_wrapper")
        self.timestamp_vlayout = QtWidgets.QVBoxLayout(self.timestamp_radio_button_wrapper)
        self.timestamp_vlayout.setContentsMargins(5, 5, 5, 5)
        self.timestamp_vlayout.setObjectName("timestamp_vlayout")
        self.timestamp_img = QtWidgets.QLabel(self.timestamp_radio_button_wrapper)
        self.timestamp_img.setEnabled(False)
        self.timestamp_img.setStyleSheet("image: url(assets/images/wizard/timestamp.png);")
        self.timestamp_img.setText("")
        self.timestamp_img.setObjectName("timestamp_img")
        self.timestamp_vlayout.addWidget(self.timestamp_img)
        self.timestamp = QtWidgets.QRadioButton(self.timestamp_radio_button_wrapper)
        self.timestamp.setEnabled(True)
        self.timestamp.setObjectName("timestamp")
        self.timestamp_vlayout.addWidget(self.timestamp)
        self.radio_buttons_hlayout.addWidget(self.timestamp_radio_button_wrapper)
        self.radio_button_group.addButton(self.timestamp, 4)


        # RADIO BUTTON VERIFY PEC
        self.pec_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.pec_radio_button_wrapper.setStyleSheet(
            "QWidget#pec_radio_button_wrapper {\n""border: 1px solid black;\n""}")
        self.pec_radio_button_wrapper.setObjectName("pec_radio_button_wrapper")
        self.pec_vlayout = QtWidgets.QVBoxLayout(self.pec_radio_button_wrapper)
        self.pec_vlayout.setContentsMargins(5, 5, 5, 5)
        self.pec_vlayout.setObjectName("pec_vlayout")
        self.pec_img = QtWidgets.QLabel(self.pec_radio_button_wrapper)
        self.pec_img.setEnabled(False)
        self.pec_img.setStyleSheet("image: url(assets/images/wizard/email.png);")
        self.pec_img.setText("")
        self.pec_img.setObjectName("pec_img")
        self.pec_vlayout.addWidget(self.pec_img)
        self.pec = QtWidgets.QRadioButton(self.pec_radio_button_wrapper)
        self.pec.setEnabled(True)
        self.pec.setObjectName("pec")
        self.pec_vlayout.addWidget(self.pec)
        self.radio_buttons_hlayout.addWidget(self.pec_radio_button_wrapper)
        self.radio_button_group.addButton(self.pec, 5)

        #AREA RECAP INFO
        self.acquisition_group_box = QtWidgets.QGroupBox(self)
        self.acquisition_group_box.setEnabled(True)
        self.acquisition_group_box.setGeometry(QtCore.QRect(130, 280, 501, 171))
        self.acquisition_group_box.setObjectName("acquisition_group_box")
        self.recap_case_info = QtWidgets.QTextBrowser(self.acquisition_group_box)
        self.recap_case_info.setGeometry(QtCore.QRect(30, 30, 430, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.recap_case_info.setFont(font)
        self.recap_case_info.setReadOnly(True)
        self.recap_case_info.setObjectName("recap_case_info")

    def isComplete(self):
        return self.radio_button_group.checkedId() >= 0


class Wizard(QtWidgets.QWizard):
    finished = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        self.width = 800
        self.height = 600
        self.setObjectName("WizardView")
        self.temp_case_info = None
        

    def init_wizard(self):
        self.setFixedSize(self.width, self.height)
        self.setSizeGripEnabled(False)
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.setTitleFormat(QtCore.Qt.RichText)
        self.setSubTitleFormat(QtCore.Qt.RichText)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join('assets/svg/', 'FIT.svg')))


        self.case_info_page = CaseInfoPage(self)
        self.select_task_page = SelectTaskPage(self)

        self.addPage(self.case_info_page)
        self.addPage(self.select_task_page)

        self.button(QtWidgets.QWizard.NextButton).clicked.connect(lambda: self.select_task_page.recap_case_info.setHtml(self._get_recap_case_info_HTML()))

        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self._save_case)

        self.button(QtWidgets.QWizard.BackButton).clicked.connect(self.__back)

        self.button(QtWidgets.QWizard.FinishButton).setDisabled(True)

        self.setButtonText(QtWidgets.QWizard.FinishButton, general.BUTTON_START)

        self.retranslateUi()
    
    def __back(self):

        if len(self.case_info_page.case_info) == 0:
            item = self.temp_case_info.get('lawyer_name')
            if item:
                self.case_info_page.form.lawyer_name.setText(item)
            item = self.temp_case_info.get('proceeding_type')
            if item:
                self.case_info_page.form.set_index_from_type_proceedings_id(item)
            item = self.temp_case_info.get('courthouse')
            if item:
                self.case_info_page.form.courthouse.setText(item)
            item = self.temp_case_info.get('proceeding_number')
            if item:
                self.case_info_page.form.proceeding_number.setText(item)
        
    
    def reload_case_info(self):
        self.case_info_page.set_case_information(self.case_info_page.form.name.currentText())
        self.select_task_page.recap_case_info.setHtml(self._get_recap_case_info_HTML())

    def _save_case(self):
        
        buttons = self.select_task_page.radio_button_group.buttons()
        selected_buttons_index = [buttons[x].isChecked() for x in range(len(buttons))].index(True)
        task = buttons[selected_buttons_index].objectName()

        case_info = {}

        if 'id' in self.case_info_page.case_info:
            case_info = self.case_info_page.case_info

        #store information case on the local DB
        try:
            if case_info:
                self.case_info_page.form.controller.cases = self.case_info_page.case_info
            else:
                case_info =  self.case_info_page.form.controller.add(self.case_info_page.case_info)
        except Exception as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Warning,
                            wizard.INSERT_UPDATE_CASE_INFO,
                            error.INSERT_UPDATE_CASE_INFO,
                            str(e)
                            )

            error_dlg.buttonClicked.connect(self.close)
            error_dlg.exec_()

        #Send signal to main loop to start the acquisition window
        self.finished.emit(task, case_info)

    def retranslateUi(self):
        self.setWindowTitle(self.__get_version())
        self.select_task_page.acquisition_group_box.setTitle(CASE_SUMMARY)
        self.select_task_page.web.setText(TASK_WEB)
        self.select_task_page.mail.setText(TASK_MAIL)
        self.select_task_page.insta.setText(TASK_INSTAGRAM)
        self.select_task_page.timestamp.setText(TASK_VERIFY_TIMESTAMP)
        self.select_task_page.pec.setText(TASK_VERIFY_PEC)
    
    def __get_version(self):
        parser = SafeConfigParser()
        parser.read('assets/config.ini')
        version = parser.get('fit_properties', 'version')
        
        return version


    def _get_recap_case_info_HTML(self):
        self.case_info_page.case_info = self.case_info_page.form.get_current_case_info()
        self.temp_case_info = self.case_info_page.case_info

        html = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        html += "<html>\n"
        html += "<head>\n"
        html += "<meta name=\"qrichtext\" content=\"1\" />\n"
        html += "<style type=\"text/css\">\n"
        html += "p, li { white-space: pre-wrap; }\n"
        html += "</style>\n"
        html += "</head>\n"
        html += "<body style=\" font-family:\'Arial\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        for keyword, value in self.case_info_page.case_info.items():
            item = self.findChild(QtWidgets.QLabel, keyword + '_label')
            if item is not None:
                if value is None:
                    value = "N/A"
                if keyword in 'proceeding_type':
                    type_proceeding = next((proceeding for proceeding in self.case_info_page.form.proceedings if proceeding["id"] == value), None)
                    if type_proceeding is not None:
                        value = type_proceeding["name"]

                label = item.text()
                html += "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px;\">\n"
                html += "<span style=\" font-family:\'Arial\',\'Courier New\',\'monospace\'; font-size:14px; font-weight:300; color:#000000;\">" + label  + ": </span>\n"
                html += "<span style=\" font-size:14px; font-weight:600;  color:#000000;\">" + str(value)  + "</span>\n"
                html += "</p>\n"
        html += "</body>\n"
        html += "</html>"

        return html
        