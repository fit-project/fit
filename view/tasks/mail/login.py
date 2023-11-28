#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import status

from common.constants.view import mail
from common.constants import error


class MailLoginWorker(QObject):
    logged_in = pyqtSignal(str)
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def login(self):
        auth_info = self.options.get("auth_info")
        controller = self.options.get("mail_controller")
        __status = status.SUCCESS

        try:
            if controller.mailbox is None:
                controller.check_server(auth_info.get("server"), auth_info.get("port"))

            if controller.is_logged_in is False:
                controller.check_login(
                    auth_info.get("email"), auth_info.get("password")
                )

        except Exception as e:
            __status = status.FAIL
            self.error.emit(
                {
                    "title": mail.SERVER_ERROR,
                    "msg": error.MAIL_SERVER_ERROR,
                    "details": str(e),
                }
            )
        except Exception as e:
            __status = status.FAIL
            self.error.emit(
                {"title": mail.LOGIN_ERROR, "msg": error.LOGIN_ERROR, "details": str(e)}
            )

        self.logged_in.emit(__status)
