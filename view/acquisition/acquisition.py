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

import os
from types import FunctionType

from common.constants import logger, state as State, status as Status, tasks as Tasks


from view.acquisition.base import Base, logging
from view.acquisition.tasks.packetcapture import AcquisitionPacketCapture
from view.acquisition.tasks.screenrecorder import AcquisitionScreenRecorder
from view.acquisition.tasks.nettools import *
from view.post_acquisition.post import PostAcquisition


from controller.configurations.tabs.packetcapture.packetcapture import PacketCapture as PacketCaptureCotroller
from controller.configurations.tabs.screenrecorder.screenrecorder import ScreenRecorder as ScreenRecorderController
from controller.configurations.tabs.general.network import Network as NetworkController

from PyQt5.QtCore import pyqtSignal

class Acquisition(Base):

    completed = pyqtSignal()

    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None) -> None:
        super().__init__(logger, progress_bar, status_bar, parent)

        self.folder = None
        self.case_info = None
        self.post_acquisition = PostAcquisition(self)
        self.post_acquisition_method_list = [x for x, y in PostAcquisition.__dict__.items() if not x.startswith("__") and type(y) == FunctionType]
        

    def start(self, tasks, folder, case_info, external_tasks=0, percent=100):

        if self.is_started:
            return
        
        #reset All
        self.info.clear_info()
        self.clear_tasks()

        
        self.total_internal_tasks = len(tasks)
        self.folder = folder
        self.case_info = case_info

        self.total_tasks = self.total_internal_tasks + external_tasks

        if self.total_tasks > 0:
            self.increment = percent/self.total_tasks

        self.log_confing.change_filehandlers_path(self.folder)
        logging.config.dictConfig(self.log_confing.config)
        self.log_start_message()

        self.is_started = True
       

        if Tasks.PACKET_CAPTURE in tasks:
            options = PacketCaptureCotroller().options
            if options['enabled']:
                options['acquisition_directory'] = self.folder
                packetcapture = AcquisitionPacketCapture(Tasks.PACKET_CAPTURE, State.STARTED, Status.PENDING, self)
                self.add_task(packetcapture)
                packetcapture.start(options)
                self.set_message_on_the_statusbar(logger.NETWORK_PACKET_CAPTURE_STARTED)
            else:
                self.total_internal_tasks -= 1

        if Tasks.SCREEN_RECORDER in tasks:
            options = ScreenRecorderController().options
            if options['enabled']:
                options['filename'] = os.path.join(self.folder, options['filename'])
                screenrecorder = AcquisitionScreenRecorder(Tasks.SCREEN_RECORDER, State.STARTED, Status.PENDING, self)
                self.add_task(screenrecorder)
                screenrecorder.start(options)
                self.set_message_on_the_statusbar(logger.SCREEN_RECODER_PACKET_CAPTURE_STARTED)
            else:
                self.total_internal_tasks -= 1

    
    def stop(self, tasks, url, external_tasks=0, percent=100):

        
        if self.is_started is False:
            return
        
        if url:
            self.log_stop_message(url)

        net_configuration = NetworkController().configuration
        self.total_internal_tasks = len(tasks)


        self.total_tasks = self.total_internal_tasks + len(self.post_acquisition_method_list) + external_tasks

        if self.total_tasks > 0:
            self.increment = percent/self.total_tasks

        
        self.set_state_and_status_tasks(State.STOPPED, Status.PENDING)

        self.is_started = False
        self.send_pyqt_signal = False

        if Tasks.WHOIS in tasks and url is not None:
            _whois = whois.AcquisitionWhois(Tasks.WHOIS, State.STARTED, Status.PENDING, self)
            self.add_task(_whois)
            self.set_message_on_the_statusbar(logger.WHOIS_GET)
            _whois.start(url)
        
        if Tasks.NSLOOKUP in tasks and url is not None:
            _nslookup = nslookup.AcquisitionNslookup(Tasks.NSLOOKUP, State.STARTED, Status.PENDING, self)
            self.add_task(_nslookup)
            self.set_message_on_the_statusbar(logger.NSLOOKUP_GET)
            _nslookup.start(url, net_configuration)

        if Tasks.HEADERS in tasks and url is not None:
            _headers = headers.AcquisitionHeaders(Tasks.HEADERS, State.STARTED, Status.PENDING, self)
            self.add_task(_headers)
            self.set_message_on_the_statusbar(logger.HEADERS_GET)
            _headers.start(url)
        
        if Tasks.TRACEROUTE in tasks and url is not None and self.folder is not None:
            _traceroute = traceroute.AcquisitionTraceroute(Tasks.TRACEROUTE, State.STARTED, Status.PENDING, self)
            self.add_task(_traceroute)
            self.set_message_on_the_statusbar(logger.TRACEROUTE_GET)
            _traceroute.start(url, self.folder)
        
        if Tasks.SSLKEYLOG in tasks and self.folder is not None:
            _sslkeylog = sslkeylog.AcquisitionSSLKeyLog(Tasks.SSLKEYLOG, State.STARTED, Status.PENDING, self)
            self.add_task(_sslkeylog)
            self.set_message_on_the_statusbar(logger.SSLKEYLOG_GET)
            _sslkeylog.start(self.folder)
        
        if Tasks.SSLCERTIFICATE in tasks and url is not None and self.folder is not None:
            _sslcertificate = sslcertificate.AcquisitionSSLCertificate(Tasks.SSLCERTIFICATE, State.STARTED, Status.PENDING, self)
            self.add_task(_sslcertificate)
            self.set_message_on_the_statusbar(logger.SSLCERTIFICATE_GET)
            _sslcertificate.start(url, self.folder)
        
        if Tasks.PACKET_CAPTURE in tasks:
            task = self.get_task(Tasks.PACKET_CAPTURE)
            if task:
                self.set_message_on_the_statusbar(logger.NETWORK_PACKET_CAPTURE_STOPPED)
                task[0].stop()
            else:
                self.total_internal_tasks -= 1

        if Tasks.SCREEN_RECORDER in tasks:
            task = self.get_task(Tasks.SCREEN_RECORDER)
            if task:
                self.set_message_on_the_statusbar(logger.SCREEN_RECODER_PACKET_CAPTURE_COMPLETED)
                task[0].stop()
            else:
                self.total_internal_tasks -= 1
      
    def task_is_completed(self, options):
        
        name = None
        state = None
        status = Status.COMPLETED
        details = ''

        if 'name' not in options:
            return
        else:
            name = options['name']
        if 'state' in options:
            state = options['state']
        if 'status' in options:
            status = options['status']
        if 'details' in options:
            details = options['details']
        
        self.update_task(name, state, status, details)
        
        self.upadate_progress_bar()
        
        if self.are_all_tasks_status_completed():
            self.completed.emit()
    

        
    
   
        