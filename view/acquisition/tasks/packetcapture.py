#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import scapy.all as scapy
import os

from PyQt5.QtCore import QObject, QEventLoop, QTimer, pyqtSignal, QThread
from PyQt5.QtWidgets import QMessageBox

from view.acquisition.base import Base
from view.acquisition.tasks.task import AcquisitionTask
from view.error import Error as ErrorView

from common.constants import logger, details, state, status, tasks
from common.constants import tasks, error

class PacketCapture(QObject):
    finished = pyqtSignal() 

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.options = None
        self.output_file = None
        self.sniffer = scapy.AsyncSniffer()

    def set_options(self, options):
        self.output_file = os.path.join(options['acquisition_directory'], options['filename'])

    def start(self):
        try:
            self.sniffer.start()
        except Exception as e:
            error_dlg = ErrorView(QMessageBox.Critical,
                                  tasks.PACKET_CAPTURE,
                                  error.PACKET_CAPTURE,
                                  str(e)
                                  )
            error_dlg.exec_()

    def stop(self):
        self.sniffer.stop()
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
        scapy.wrpcap(self.output_file, self.sniffer.results)
        self.finished.emit()



class AcquisitionPacketCapture(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, options):
        
        self.th_packetcapture = QThread()
        self.packetcapture = PacketCapture()
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