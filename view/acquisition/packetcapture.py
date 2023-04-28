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
from view.packetcapture import PacketCapture as PacketCaptureView

from PyQt5 import QtCore

class AcquisitionPacketCapture(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, options):
        
        self.th_packetcapture = QtCore.QThread()
        self.packetcapture = PacketCaptureView()
        self.packetcapture.set_options(options)
        self.packetcapture.moveToThread(self.th_packetcapture)

        self.th_packetcapture.started.connect(self.packetcapture.start)
        self.packetcapture.finished.connect(self.th_packetcapture.quit)
        self.packetcapture.finished.connect(self.packetcapture.deleteLater)
        self.th_packetcapture.finished.connect(self.th_packetcapture.deleteLater)
        self.th_packetcapture.finished.connect(self._thread_packetcapture_is_finished)

        self.th_packetcapture.start()
        
        self.parent().logger.info(logger.NETWORK_PACKET_CAPTURE_STARTED)
        self.parent().task_is_completed({
                                'name' : tasks.PACKET_CAPTURE,
                                'details' : details.NETWORK_PACKET_CAPTURE_STARTED
                            })

    def stop(self):
        self.packetcapture.stop()
 

    def _thread_packetcapture_is_finished(self):
        self.parent().logger.info(logger.NETWORK_PACKET_CAPTURE_COMPLETED)
        self.parent().task_is_completed({
                                'name' : tasks.PACKET_CAPTURE,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED,
                                'details' : details.NETWORK_PACKET_CAPTURE_COMPLETED
                                })