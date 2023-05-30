#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os
from PyQt6 import QtCore

from common.utility import traceroute
from common.constants import logger as Logger, state, status, tasks

from view.acquisition.tasks.task import AcquisitionTask

class TracerouteWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, url, folder):
        super().__init__()
        self.url = url
        self.folder = folder
    
    @QtCore.pyqtSlot()
    def run(self):
        traceroute(self.url, os.path.join(self.folder, 'traceroute.txt'))
        self.finished.emit()

class AcquisitionTraceroute(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, url, folder):
        self.thread_worker= QtCore.QThread()
        self.worker = TracerouteWorker(url, folder)
        
        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread_worker.quit)
        
        self.thread_worker.finished.connect(self.__thread_worker_is_finished)

        self.thread_worker.start()
    
    def __thread_worker_is_finished(self):
        self.parent().logger.info(Logger.TRACEROUTE_GET)
        self.parent().task_is_completed({
                                'name' : tasks.TRACEROUTE,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED
                            })
                            