#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2022 FIT-Project and others
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

import datetime
import logging
import os


# Produce RFC 3339 timestamps
logging.Formatter.formatTime = (lambda self, record, datefmt: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat())

class LogConfig:
    def __init__(self):

        self.config = {
            'version': 1,
            'disable_existing_loggers': True,
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
                'whois': {
                    'class': 'logging.Formatter',
                    'format': '%(message)s'
                },
                'headers': {
                    'class': 'logging.Formatter',
                    'format': '%(message)s'
                }

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
                'fwhois': {
                    'class': 'logging.FileHandler',
                    'filename': 'whois.txt',
                    'mode': 'w',
                    'formatter': 'whois',
                },
                'fheaders': {
                    'class': 'logging.FileHandler',
                    'filename': 'headers.txt',
                    'mode': 'w',
                    'formatter': 'headers',
                }
            },
            'loggers': {
                'view.web': {
                    'handlers': ['facquisition'],
                    'level' : 'INFO'
                },
                'hashreport': {
                    'handlers': ['fhashreport'],
                    'level' : 'INFO'
                },
                'view.mail': {
                    'handlers': ['facquisition'],
                    'level': 'INFO'
                },
                'whois': {
                    'handlers': ['fwhois'],
                    'level' : 'INFO'
                },
                'headers': {
                    'handlers': ['fheaders'],
                    'level' : 'INFO'
                }
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
                handler['filename'] = os.path.join(path, handler['filename'])

    def disable_loggers(self, loggers):
        for logger in loggers:
            for handler in logger.handlers.copy():
                logger.removeHandler(handler)
            logger.addHandler(logging.NullHandler())
            logger.propagate = False

class LogConfigMail:
    def __init__(self):

        self.config = {
            'version': 1,
            'disable_existing_loggers': True,
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
                    'level' : 'INFO'
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
                handler['filename'] = os.path.join(path, handler['filename'])

    def disable_loggers(self, loggers):
        for logger in loggers:
            for handler in logger.handlers.copy():
                logger.removeHandler(handler)
            logger.addHandler(logging.NullHandler())
            logger.propagate = False