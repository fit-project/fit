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
import subprocess
from view.error import Error as ErrorView
from PyQt5 import QtWidgets
from common.error import ErrorMessage

class verifyPec:
    def __init__(self):
        self.error_msg = ErrorMessage()
        return

    def verifyPec(self, path):
        eml_file_path = path

        # Estrai la firma digitale dal file EML
        result = subprocess.call(
            ['openssl', 'smime', '-verify', '-in', eml_file_path, '-noverify', '-out', 'signature.txt'],
            stdout=subprocess.PIPE)

        if result == 0:
            # Stampa l'output del comando
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['pec_verified'],
                                  self.error_msg.MESSAGES['pec_verified'],
                                  'PEC has a valid signature')
            error_dlg.exec_()
        else:
            # Stampa l'output del comando
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['pec_not_verified'],
                                  self.error_msg.MESSAGES['pec_not_verified'],
                                  'PEC has an invalid signature')
            error_dlg.exec_()



