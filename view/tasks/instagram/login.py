#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from instaloader import (
    InvalidArgumentException,
    BadCredentialsException,
    ConnectionException,
    ProfileNotExistsException,
)

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import status

from common.constants.view import instagram
from common.constants import error


class InstagramLoginWorker(QObject):
    logged_in = pyqtSignal(str, int)
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def login(self):
        auth_info = self.options.get("auth_info")
        controller = self.options.get("instagram_controller")
        __status = status.SUCCESS
        __account_type = 0

        controller.set_login_information(
            auth_info.get("username"),
            auth_info.get("password"),
            auth_info.get("profile"),
        )

        if controller.is_logged_in is False:
            try:
                controller.login()
            except InvalidArgumentException as e:
                __status = status.FAIL
                self.error.emit(
                    {
                        "title": instagram.INVALID_USER,
                        "msg": error.INVALID_USER,
                        "details": str(e),
                    }
                )
            except BadCredentialsException as e:
                __status = status.FAIL
                self.error.emit(
                    {
                        "title": instagram.LOGIN_ERROR,
                        "msg": error.PASSWORD_ERROR,
                        "details": str(e),
                    }
                )
            except ConnectionException as e:
                __status = status.FAIL
                self.error.emit(
                    {
                        "title": instagram.CONNECTION_ERROR,
                        "msg": error.LOGIN_ERROR,
                        "details": str(e),
                    }
                )
            except ProfileNotExistsException as e:
                __status = status.FAIL
                self.error.emit(
                    {
                        "title": instagram.INVALID_PROFILE,
                        "msg": error.INVALID_PROFILE,
                        "details": str(e),
                    }
                )
            except Exception as e:
                __status = status.FAIL
                self.error.emit(
                    {
                        "title": instagram.SERVER_ERROR,
                        "msg": error.GENERIC_ERROR,
                        "details": str(e),
                    }
                )
            else:
                __account_type = controller.check_account()

        self.logged_in.emit(__status, __account_type)
