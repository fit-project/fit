#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import numpy as np
from PIL import Image


from PyQt6.QtCore import QObject, QEventLoop, QTimer, pyqtSignal


from view.util import screenshot_filename


class FullPageScreenShot(QObject):
    def __init__(
        self,
        current_widget,
        acquisition_directory=None,
        screenshot_directory=None,
        parent=None,
    ):
        super().__init__(parent)

        self.current_widget = current_widget
        self.screenshot_directory = screenshot_directory
        self.acquisition_directory = acquisition_directory
        self.is_running_task = False

    @property
    def is_running_task(self):
        return self._is_running_task

    @is_running_task.setter
    def is_running_task(self, is_running_task):
        self._is_running_task = is_running_task

    def take_screenshot(self):
        if self.screenshot_directory is not None:
            full_page_folder = os.path.join(
                self.screenshot_directory
                + "/full_page/{}/".format(self.current_widget.url().host())
            )
            if not os.path.isdir(full_page_folder):
                os.makedirs(full_page_folder)

            # move page on top
            self.current_widget.page().runJavaScript("window.scrollTo(0, 0);")

            next = 0
            part = 0
            step = self.current_widget.height()
            end = self.current_widget.page().contentsSize().toSize().height()
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec()

            images = []

            while next < end:
                filename = screenshot_filename(full_page_folder, "part_" + str(part))
                if next == 0:
                    self.current_widget.grab().save(filename)
                else:
                    self.current_widget.page().runJavaScript(
                        "window.scrollTo({}, {});".format(0, next)
                    )

                    ### Waiting everything is synchronized
                    loop = QEventLoop()
                    QTimer.singleShot(500, loop.quit)
                    loop.exec()
                    self.current_widget.grab().save(filename)

                images.append(filename)

                part += 1
                next += step

            # combine all images part in an unique image
            imgs = [Image.open(i) for i in images]
            # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
            min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]

            # for a vertical stacking it is simple: use vstack
            imgs_comb = np.vstack([i.resize(min_shape) for i in imgs])
            imgs_comb = Image.fromarray(imgs_comb)

            whole_img_filename = screenshot_filename(
                self.screenshot_directory, "full_page" + ""
            )
            if self.is_running_task:
                whole_img_filename = os.path.join(
                    self.acquisition_directory, "screenshot.png"
                )

            imgs_comb.save(whole_img_filename)
