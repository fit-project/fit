#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck as NetworkCheckController
from controller.configurations.tabs.network.networktools import NetworkTools as NetworkToolsController


from common.utility import is_npcap_installed, get_platform

from PyQt6.QtCore import pyqtSignal

class Acquisition(Base):

    completed = pyqtSignal()

    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None) -> None:
        super().__init__(logger, progress_bar, status_bar, parent)

        self.folder = None
        self.case_info = None
        self.post_acquisition = PostAcquisition(self)
        self.post_acquisition_method_list = [x for x, y in PostAcquisition.__dict__.items() if not x.startswith("__") and type(y) == FunctionType]
        

    def __remove_disable_tasks(self, tasks):
        _tasks = tasks.copy()
        for task in tasks:
            if task == Tasks.PACKET_CAPTURE and PacketCaptureCotroller().options['enabled'] is False or\
               task == Tasks.SCREEN_RECORDER and ScreenRecorderController().options['enabled'] is False or\
               task == Tasks.SSLKEYLOG and NetworkToolsController().configuration['ssl_keylog'] is False or\
               task == Tasks.SSLCERTIFICATE and NetworkToolsController().configuration['ssl_certificate'] is False or\
               task == Tasks.HEADERS and NetworkToolsController().configuration['headers'] is False or\
               task == Tasks.WHOIS and NetworkToolsController().configuration['whois'] is False or\
               task == Tasks.NSLOOKUP and NetworkToolsController().configuration['nslookup'] is False or\
               task == Tasks.TRACEROUTE and NetworkToolsController().configuration['traceroute'] is False or\
               get_platform() == 'win' and is_npcap_installed() is False:
                _tasks.remove(task)
        
        return _tasks
    
    def start(self, tasks, folder, case_info, external_tasks=0, percent=100):

        if self.is_started:
            return
        
        #reset All
        self.info.clear_info()
        self.clear_tasks()

        self.folder = folder
        self.case_info = case_info

        if self.logger.name == 'view.web.web':
            self.log_confing.set_dynamic_loggers()

        self.log_confing.change_filehandlers_path(self.folder)
        logging.config.dictConfig(self.log_confing.config)
        self.log_start_message()

        self.is_started = True

        tasks = self.__remove_disable_tasks(tasks)
        self.total_internal_tasks = len(tasks)
        self.total_tasks = self.total_internal_tasks + external_tasks


        if self.total_tasks > 0:
            self.increment = percent/self.total_tasks
        else:
           self.completed.emit()

       
        if Tasks.PACKET_CAPTURE in tasks:
            options = PacketCaptureCotroller().options
            options['acquisition_directory'] = self.folder
            packetcapture = AcquisitionPacketCapture(Tasks.PACKET_CAPTURE, State.STARTED, Status.PENDING, self)
            self.add_task(packetcapture)
            packetcapture.start(options)
            self.set_message_on_the_statusbar(logger.NETWORK_PACKET_CAPTURE_STARTED)

        if Tasks.SCREEN_RECORDER in tasks:
            options = ScreenRecorderController().options
            options['filename'] = os.path.join(self.folder, options['filename'])
            screenrecorder = AcquisitionScreenRecorder(Tasks.SCREEN_RECORDER, State.STARTED, Status.PENDING, self)
            self.add_task(screenrecorder)
            screenrecorder.start(options)
            self.set_message_on_the_statusbar(logger.SCREEN_RECODER_PACKET_CAPTURE_STARTED)

    
    def stop(self, tasks, url, external_tasks=0, percent=100):

        
        if self.is_started is False:
            return
        
        if url:
            self.log_stop_message(url)

        net_configuration = NetworkCheckController().configuration

        self.set_state_and_status_tasks(State.STOPPED, Status.PENDING)

        self.is_started = False
        self.send_pyqt_signal = False

        tasks = self.__remove_disable_tasks(tasks)
        self.total_internal_tasks = len(tasks)
        self.total_tasks = self.total_internal_tasks + len(self.post_acquisition_method_list) + external_tasks

        if self.total_tasks > 0:
            self.increment = percent/self.total_tasks
        else:
           self.completed.emit()

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

        if Tasks.SCREEN_RECORDER in tasks:
            task = self.get_task(Tasks.SCREEN_RECORDER)
            if task:
                self.set_message_on_the_statusbar(logger.SCREEN_RECODER_PACKET_CAPTURE_COMPLETED)
                task[0].stop()
    
      
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
    

        
    
   
        