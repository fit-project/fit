#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os

from view.acquisition.acquisition import Acquisition
from view.acquisition.tasks.task import AcquisitionTask
from view.acquisition.tasks.screenrecorder import AcquisitionScreenRecorder
from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderController,
)

from common.constants import logger, state as State, status as Status, tasks as Tasks


class AcquisitionManager:
    def __init__(self, logger, progress_bar, status_bar, parent):
        self.acquisition = Acquisition(logger, progress_bar, status_bar, self)

    def start_task_screen_recorder(self):
        options = ScreenRecorderController().options

        if options["enabled"] is True:
            options["filename"] = os.path.join(
                self.acquisition.folder, options["filename"]
            )
            self.screen_recorder_task = AcquisitionScreenRecorder(
                Tasks.SCREEN_RECORDER, State.STARTED, Status.PENDING, self
            )
            self.acquisition.info.add_task(
                self.screen_recorder_task.name,
                self.screen_recorder_task.state,
                self.screen_recorder_task.status,
                "",
            )
            self.screen_recorder_task.finished.connect(self.__task_complete(options))
            self.screen_recorder_task.start(options)
            self.acquisition.set_message_on_the_statusbar(
                logger.SCREEN_RECODER_PACKET_CAPTURE_STARTED
            )

    def __task_complete(self, options):
        print(options)
