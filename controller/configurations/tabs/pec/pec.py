#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from model.configurations.tabs.pec.pec import Pec as PecModel

class Pec():

    def __init__(self):
        self.model = PecModel()
        self._options = self.model.get()
        if self._options:
           self._options = {key: value for key, value in self._options[0].__dict__.items() if not key.startswith("_") and not key.startswith("__") and not key.startswith("db")}

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self.model.update(options)

