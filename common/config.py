#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import datetime
import logging
import os

from controller.configurations.tabs.network.networktools import NetworkTools as NetworkToolsController


# Produce RFC 3339 timestamps
logging.Formatter.formatTime = (lambda self, record, datefmt: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat())


class LogConfigTools:
    def __init__(self):

        self.config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'class': 'logging.Formatter',
                    'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
                },
                'hashreport': {
                    'class': 'logging.Formatter',
                    'format': '%(message)s'
                },
                'acquisition': {
                    'class': 'logging.Formatter',
                    'format': '%(asctime)s - %(message)s'
                },

            },
            'handlers': {
                "null": {
                    "class": "logging.NullHandler"
                },
                'facquisition': {
                    'class': 'logging.FileHandler',
                    'filename': 'acquisition.log',
                    'mode': 'w',
                    'formatter': 'acquisition',
                },
                'fhashreport': {
                    'class': 'logging.FileHandler',
                    'filename': 'acquisition.hash',
                    'mode': 'w',
                    'formatter': 'hashreport',
                },
            },
            'loggers': {
                'view.web': {
                    'handlers': ['facquisition'],
                    'level': 'INFO'
                },
                'view.instagram': {
                    'handlers': ['facquisition'],
                    'level': 'INFO'
                },
                'view.video': {
                    'handlers': ['facquisition'],
                    'level': 'INFO'
                },
                'hashreport': {
                    'handlers': ['fhashreport'],
                    'level' : 'INFO'
                },
                'view.mail': {
                    'handlers': ['facquisition'],
                    'level': 'INFO'
                },
            },
            'root': {
                'handlers': ['null'],
                "propagate": False
            }
        }

    def change_filehandlers_path(self, path, exclude=None):
        for key in self.config['handlers']:
            handler = self.config['handlers'][key]
            if 'filename' in handler.keys():
                stripped = handler['filename'].split("\\")[-1]
                if stripped:
                    handler['filename'] = os.path.join(path, stripped)
                else:
                    handler['filename'] = os.path.join(path, handler['filename'])

    def disable_loggers(self, loggers):
        for logger in loggers:
            for handler in logger.handlers.copy():
                logger.removeHandler(handler)
            logger.addHandler(logging.NullHandler())
            logger.propagate = False

    def set_web_loggers(self):
        if NetworkToolsController().configuration['whois']:
            self.config['formatters']['whois'] = {'class': 'logging.Formatter', 'format': '%(message)s'}
            self.config['handlers']['fwhois'] = {'class': 'logging.FileHandler', 'filename': 'whois.txt', 'mode': 'w',
                                            'formatter': 'whois'}
            self.config['loggers']['whois'] = {'handlers': ['fwhois'], 'level': 'INFO'}

        if NetworkToolsController().configuration['headers']:
            self.config['formatters']['headers'] = {'class': 'logging.Formatter', 'format': '%(message)s'}
            self.config['handlers']['fheaders'] = {'class': 'logging.FileHandler', 'filename': 'headers.txt', 'mode': 'w',
                                              'formatter': 'headers'}
            self.config['loggers']['headers'] = {'handlers': ['fheaders'], 'level': 'INFO'}

        if NetworkToolsController().configuration['nslookup']:
            self.config['formatters']['nslookup'] = {'class': 'logging.Formatter', 'format': '%(message)s'}
            self.config['handlers']['fnslookup'] = {'class': 'logging.FileHandler', 'filename': 'nslookup.txt', 'mode': 'w',
                                               'formatter': 'nslookup'}
            self.config['loggers']['nslookup'] = {'handlers': ['fnslookup'], 'level': 'INFO'}