#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtWidgets

from view.dialog import Dialog, DialogButtonTypes
from view.clickable_label import ClickableLabel as ClickableLabelView
from view.checks.check import Check

from common.utility import is_nvidia_gpu_installed

from common.constants.view.tasks import status
from common.constants.view.initial_checks import (
    NVIDIA_GPU_PRESENT_TITLE,
    NVIDIA_GPU_PRESENT_MSG,
    NVIDIA_GPU_GUIDE_URL,
    NVIDIA_GPU_GUIDE,
)


class NvidiaGPUInstalledCheck(Check):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run_check(self):
        if is_nvidia_gpu_installed():
            dialog = Dialog(
                NVIDIA_GPU_PRESENT_TITLE,
                NVIDIA_GPU_PRESENT_MSG,
                "",
                QtWidgets.QMessageBox.Icon.Warning,
            )
            dialog.message.setStyleSheet("font-size: 13px;")
            dialog.set_buttons_type(DialogButtonTypes.MESSAGE)
            dialog.right_button.clicked.connect(lambda: dialog.close())
            dialog.right_button.clicked.connect(
                lambda: self.finished.emit(status.SUCCESS)
            )
            dialog.text_box.addWidget(
                ClickableLabelView(NVIDIA_GPU_GUIDE_URL, NVIDIA_GPU_GUIDE)
            )

            dialog.content_box.adjustSize()

            dialog.exec()
        else:
            self.finished.emit(status.SUCCESS)
