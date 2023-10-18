# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os

from PyQt6 import QtCore, QtWidgets, QtGui

from view.post_acquisition.pec.search_pec import SearchPec as SearchPecView

from common.utility import resolve_path
from common.constants.view.pec import eml_not_found
from common.constants.status import *


class EmlNotFound(QtWidgets.QDialog):
    def __init__(self, directory, case_info, attempts):
        super().__init__()

        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.search = SearchPecView()
        self.directory = directory
        self.case_info = case_info
        self.attempts = attempts

        self.setObjectName("eml_not_found")
        self.resize(200, 100)
        self.setWindowTitle("Freezing Internet Tool")

        self.setWindowIcon(
            QtGui.QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg"))
        )
        buttons = (
            QtWidgets.QDialogButtonBox.StandardButton.Yes
            | QtWidgets.QDialogButtonBox.StandardButton.No
        )

        self.buttonBox = QtWidgets.QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.__close)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel(eml_not_found.MESSAGE.format(self.attempts))
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self):
        self.hide()
        self.search.init(self.case_info, self.directory)
        self.search.exec()

    def __close(self):
        self.search.downloadedeml.emit(FAIL)
        self.reject()
