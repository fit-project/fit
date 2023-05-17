#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import cv2
import pyautogui
import numpy as np
import sys

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox

from view.acquisition.base import Base
from view.acquisition.tasks.task import AcquisitionTask
from view.error import Error as ErrorView


from controller.configurations.tabs.screenrecorder.codec import Codec as CodecController
from common.constants import logger, details, state, status, tasks
from common.constants import error
from common.constants.view import screenrecorder


class ScreenRecorder(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.run = True
        self.destroyed.connect(self.stop)
        self.controller = CodecController()
        
    def set_options(self, options):

        
        # Specify resolution
        self.resolution = (pyautogui.size())

        # Specify video codec       
        codec = next((item for item in self.controller.codec if item["id"] == options['codec_id']))
        self.codec = cv2.VideoWriter_fourcc(*codec["name"])

        # Specify frames rate. We can choose any
        # value and experiment with it
        self.fps = options['fps']

        # Specify name of Output file
        self.filename = options['filename']
        
    def start(self):
        #Creating a VideoWriter object
        self.out = cv2.VideoWriter(self.filename, self.codec, self.fps, self.resolution)
        try:
            while self.run:
                #Take screenshot using PyAutoGUI
                img = pyautogui.screenshot()

                #Convert the screenshot to a numpy array
                frame = np.array(img)

                #Convert it from BGR(Blue, Green, Red) to RGB(Red, Green, Blue)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                #Write it to the output file
                self.out.write(frame)

        except:
                error_dlg = ErrorView(QMessageBox.Critical,
                            screenrecorder.SCREEN_RECODER,
                            error.SCREEN_RECODER,
                            str(sys.exc_info()[0])
                            )
                
                error_dlg.exec_()

        #Release the Video writer
        self.out.release()

        self.finished.emit()  # emit the finished signal when the loop is done
        #Destroy all windows
        cv2.destroyAllWindows()

    def stop(self):
        self.run = False  # set the run condition to false on stop 



class AcquisitionScreenRecorder(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, options):
        
        self.th_screenrecorder = QThread()
        self.screenrecorder = ScreenRecorder()
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
        self.parent().logger.info(logger.SCREEN_RECODER_PACKET_CAPTURE_COMPLETED)

        self.parent().task_is_completed({
                                'name' : tasks.SCREEN_RECORDER,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED,
                                'details' : details.SCREEN_RECORDER_COMPLETED
                            })
        

        