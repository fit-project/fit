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

from PyQt5 import QtCore, QtGui, QtWidgets

import sys
import re


import view.configurations
import pkgutil
from inspect import isclass
from importlib import import_module

class Configuration(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Configuration, self).__init__(parent)

        self.setObjectName("ConfigurationView")
        self.resize(722, 480)

        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setGeometry(QtCore.QRect(0, 0, 721, 431))
        self.tabs.setObjectName("tabs")

        self.load_tabs()
        self.retranslateUi()

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(520, 440, 192, 28))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Configuration", "Fit Configuration"))


    def load_tabs(self):
        package=view.configurations
        for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__, prefix=package.__name__+'.', onerror=lambda x: None):

           
            
            #import module if not loaded
            if modname not in sys.modules and not ispkg:
                import_module(modname)

            if modname in sys.modules and not ispkg:
                
                #find class name in a module 
                class_name = [x for x in dir(sys.modules[modname]) if isclass(getattr(sys.modules[modname], x)) and 
                                getattr(sys.modules[modname], '__is_tab__') and x.lower() == modname.rsplit( ".", 1 )[ 1 ]]

                if class_name:
                    tab = getattr(sys.modules[modname], class_name[0])
                    tab = tab()
                    self.tabs.addTab(tab, tab.windowTitle())
    
    def accept(self) -> None:
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            tab.accept()

        return super().accept()
    
    def get_tab_from_name(self, name):
         for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)

            if tab.objectName() == name:
                return tab

    
    def reject(self) -> None:
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            tab.reject()
            
        return super().reject()