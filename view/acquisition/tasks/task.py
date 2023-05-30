#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt6.QtCore import QObject

class AcquisitionTask(QObject):
    def __init__(self, name, state, status, parent=None):
        super().__init__(parent)
        self.name = name
        self.state = state
        self.status = status