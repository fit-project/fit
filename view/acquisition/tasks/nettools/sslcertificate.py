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

from common.utility import (
    check_if_peer_certificate_exist,
    get_peer_PEM_cert,
    save_PEM_cert_to_CER_cert,
)
from common.constants import (
    logger as Logger,
    state,
    status as Status,
    tasks,
    details as Details,
)

from view.acquisition.tasks.task import AcquisitionTask


class AcquisitionSSLCertificate(AcquisitionTask):
    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, url, folder):
        details = ""

        if check_if_peer_certificate_exist(url):
            certificate = get_peer_PEM_cert(url)
            save_PEM_cert_to_CER_cert(os.path.join(folder, "server.cer"), certificate)
        else:
            details = Details.SSLCERTIFICATE_NOT_EXIST

        self.parent().logger.info(Logger.SSLCERTIFICATE_GET)
        self.parent().task_is_completed(
            {
                "name": tasks.SSLCERTIFICATE,
                "state": state.FINISHED,
                "status": Status.COMPLETED,
                "details": details,
            }
        )
        self.deleteLater()
