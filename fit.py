#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

import sys

from fit_common.core import resolve_path
from fit_wizard.view.wizard import Wizard
from PySide6 import QtGui, QtWidgets


def main():
    def start_task(task, case_info):
        print(f"task: {task}")
        print(f"case_info: {case_info}")
        window.close()

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resolve_path("icon.ico")))
    window = Wizard()
    window.finished.connect(lambda task, case_info: start_task(task, case_info))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
