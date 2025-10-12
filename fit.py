#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

from PySide6.QtWidgets import QApplication
import sys

from fit_wizard.view.wizard import Wizard


def main():
    def start_task(task, case_info):
        print(f"task: {task}")
        print(f"case_info: {case_info}")
        window.close()

    app = QApplication(sys.argv)
    window = Wizard()
    window.finished.connect(lambda task, case_info: start_task(task, case_info))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
