#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

import argparse
import sys

from fit_common.core import (
    DebugLevel,
    debug,
    resolve_path,
    set_debug_level,
    set_gui_crash_handler,
)
from fit_web.web import Web
from fit_wizard.view.wizard import Wizard
from PySide6 import QtGui, QtWidgets


def parse_args():
    parser = argparse.ArgumentParser(description="FIT")
    parser.add_argument(
        "--debug",
        choices=["none", "log", "verbose"],
        default="none",
        help="Set the debug level (default: none)",
    )
    return parser.parse_args()


def show_crash_dialog(error_message: str):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    msg_box.setWindowTitle("Application Error")
    msg_box.setText("A fatal error occurred:")
    msg_box.setDetailedText(error_message)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec()


def main():
    def start_task():
        task = None
        if wizard.selcted_task == "web":
            task = Web(wizard)

        if task is not None and task.has_valid_case:
            wizard.hide()
            task.show()
        else:
            debug(
                "User cancelled the case form. Nothing to display.",
                context="Main.fit_web",
            )
            sys.exit(0)

    args = parse_args()
    set_debug_level(
        {
            "none": DebugLevel.NONE,
            "log": DebugLevel.LOG,
            "verbose": DebugLevel.VERBOSE,
        }[args.debug]
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resolve_path("icon.ico")))

    set_gui_crash_handler(show_crash_dialog)

    wizard = Wizard()
    wizard.finished.connect(start_task)
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
