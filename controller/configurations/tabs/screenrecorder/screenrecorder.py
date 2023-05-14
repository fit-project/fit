#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from model.configurations.tabs.screenrecorder.screenrecorder import ScreenRecorder as ScreenRecorderModel

class ScreenRecorder():
    _options = {}

    def __init__(self):
      self.model = ScreenRecorderModel()
      self._options = self.model.get()

    

    @property
    def options(self):
      return {key: value for key, value in self._options[0].__dict__.items() if not key.startswith("_") and not key.startswith("__") and not key.startswith("db")}


    @options.setter
    def options(self, options):
      self.model.update(options)