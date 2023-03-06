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

from model.configurations.tabs.pec.pec import Pec as PecModel

class Pec():

    _options = {}

    def __init__(self):
        self.model = PecModel()
        _options = self.model.get()

    def add(self, pec, password, server, port, serverImap, portImap):
        self.model.add(pec, password, server, port, serverImap, portImap)

    def delete(self, pecData):
        self.model.delete(pecData)

    def update(self, pecData, passwordData, serverData, portData, serverImapData, portImapData):
        self.model.update(pecData, passwordData, serverData, portData, serverImapData, portImapData)

    def get(self):
        return self.model.get()

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self.model.update(options)

