#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2023 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 

from common.constants import logger, details, state, status, tasks

from PyQt5 import QtCore

from view.acquisition.base import Base
from view.acquisition.task import AcquisitionTask
from view.screenrecorder import ScreenRecorder as ScreenRecorderView

from PyQt5 import QtCore

class AcquisitionScreenRecorder(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, options):
        
        self.th_screenrecorder = QtCore.QThread()
        self.screenrecorder = ScreenRecorderView()
        self.screenrecorder.set_options(options)

        self.screenrecorder.moveToThread(self.th_screenrecorder)

        self.th_screenrecorder.started.connect(self.screenrecorder.start)

        self.screenrecorder.finished.connect(self.th_screenrecorder.quit)
        self.screenrecorder.finished.connect(self.screenrecorder.deleteLater)
        self.th_screenrecorder.finished.connect(self.th_screenrecorder.deleteLater)
        self.th_screenrecorder.finished.connect(self._thread_screenrecorder_is_finished)

        self.th_screenrecorder.start()

        self.parent().task_is_completed({
                                'name' : tasks.SCREEN_RECORDER,
                                'details' : details.SCREEN_RECORDER_STARTED
                            })

    def stop(self):
        self.screenrecorder.stop()

    def _thread_screenrecorder_is_finished(self):
        self.th_screenrecorder.quit()
        self.th_screenrecorder.wait()
        self.parent().logger.info(logger.SCREEN_RECODER_PACKET_CAPTURE_COMPLETED)

        self.parent().task_is_completed({
                                'name' : tasks.SCREEN_RECORDER,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED,
                                'details' : details.SCREEN_RECORDER_COMPLETED
                            })
        

        