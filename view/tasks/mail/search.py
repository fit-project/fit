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


class MailSearchWorker(QObject):
    search_emails_finished = pyqtSignal(str, dict)
    search_statistics = pyqtSignal(dict)
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def search(self):
        __status = status.SUCCESS
        emails = {}

        search_criteria = self.options.get("search_criteria")
        controller = self.options.get("mail_controller")

        if search_criteria:
            search_criteria = controller.set_criteria(
                search_criteria.get("sender"),
                search_criteria.get("recipient"),
                search_criteria.get("subject"),
                search_criteria.get("from_date"),
                search_criteria.get("to_date"),
            )

        try:
            self.search_statistics.emit(
                controller.get_search_statistics(search_criteria)
            )
        except Exception as e:
            self.error.emit(
                {
                    "title": mail.GET_SEARCH_STATISTICS_ERROR,
                    "msg": mail.GET_SEARCH_STATISTICS_ERROR,
                    "details": str(e),
                }
            )
            __status = status.FAIL
        else:
            try:
                emails = controller.get_mails_from_every_folder(search_criteria)
            except Exception as e:  # Get mails
                __status = status.FAIL
                self.error.emit(
                    {
                        "title": mail.SEARCH_ERROR,
                        "msg": mail.SEARCH_ERROR,
                        "details": str(e),
                    }
                )

        self.search_emails_finished.emit(__status, emails)
