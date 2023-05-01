# !/usr/bin/env python3
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


from PyQt5 import QtCore, QtWidgets

from view.post_acquisition.pec.search_pec import SearchPec as SearchPecView
from common.constants.view.pec import eml_not_found
from common.constants.status import *


class EmlNotFound(QtWidgets.QDialog):
    def __init__(self, directory, case_info, attempts):
        super().__init__()

        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.search = SearchPecView()
        self.directory = directory
        self.case_info = case_info
        self.attempts = attempts

        self.setObjectName("eml_not_found")
        self.resize(200, 100)

        buttons = QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No

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
        self.search.exec_()
        

    def __close(self):
        self.search.downloadedeml.emit(FAIL)
        self.reject()
        
