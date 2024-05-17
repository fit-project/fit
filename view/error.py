#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
from view.dialog import Dialog


class Error(Dialog):
    def __init__(self, severity, title, message, details, parent=None):
        super().__init__(title, message, details, severity, parent)
        self.right_button.clicked.connect(self.close)
