#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox

from view.tasks.mail.login import MailLogin
from view.tasks.mail.search import MailSearch
from view.tasks.mail.download import MailDownload

from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.mail import Mail as MailController

from common.constants.view.tasks import labels, state, status
from common.constants import logger


class TaskMail(Task):
    logged_in = pyqtSignal(str)
    search_emails_finished = pyqtSignal(str, dict)
    download_finished = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.MAIL_SCRAPER
        self.sub_task = None
        self.sub_task_thread = None
        self.sub_tasks = [
            {
                "label": labels.LOGGED_IN,
                "state": self.state,
                "status": self.status,
            },
            {
                "label": labels.SEARCH_EMAILS,
                "state": self.state,
                "status": self.status,
            },
            {
                "label": labels.DOWNLOAD_EMAILS,
                "state": self.state,
                "status": self.status,
            },
        ]

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.MAIL_SCRAPER_STARTED)
        self.logger.info(logger.MAIL_SCRAPER_STARTED)
        self.options["mail_controller"] = MailController()

        self.__started()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def login(self):
        self.sub_task = MailLogin()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.login)
        self.sub_task.logged_in.connect(self.__logged_in)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options

        self.sub_task_thread.start()

    def __logged_in(self, __status):
        sub_task_logged_in = next(
            (task for task in self.sub_tasks if task.get("label") == labels.LOGGED_IN),
            None,
        )
        if sub_task_logged_in:
            sub_task_logged_in["state"] = state.COMPLETED
            sub_task_logged_in["status"] = __status

        self.logger.info(
            logger.MAIL_SCRAPER_LOGGED_IN.format(
                self.options["auth_info"].get("email"), __status
            )
        )
        self.set_message_on_the_statusbar(
            logger.MAIL_SCRAPER_LOGGED_IN.format(
                self.options["auth_info"].get("email"), __status
            )
        )

        self.logged_in.emit(__status)

        self.__quit_to_sub_task()

    def search(self):
        self.sub_task = MailSearch()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.search)
        self.sub_task.search_emails_finished.connect(self.__search_emails_finished)
        self.sub_task.search_statistics.connect(self.__search_statistics_handler)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task_thread.start()

        self.logger.info(
            logger.MAIL_SCRAPER_SEARCH_CRITERIA.format(
                str(self.options["search_criteria"])
            )
        )

    def __search_emails_finished(self, __status, emails):
        sub_task_search_mails = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.SEARCH_EMAILS
            ),
            None,
        )
        if sub_task_search_mails:
            sub_task_search_mails["state"] = state.COMPLETED
            sub_task_search_mails["status"] = __status

        self.logger.info(logger.MAIL_SCRAPER_SEARCH_EMAILS.format(__status))
        self.set_message_on_the_statusbar(
            logger.MAIL_SCRAPER_SEARCH_EMAILS.format(__status)
        )

        self.search_emails_finished.emit(__status, emails)

        self.__quit_to_sub_task()

    def __search_statistics_handler(self, statistics):
        self.logger.info(
            logger.MAIL_SCRAPER_FETCH_EMAILS.format(
                statistics.get("estimated_time"), statistics.get("total_emails")
            )
        )
        self.set_message_on_the_statusbar(
            logger.MAIL_SCRAPER_FETCH_EMAILS.format(
                statistics.get("estimated_time"), statistics.get("total_emails")
            )
        )

    def download(self):
        self.sub_task = MailDownload()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.download)
        self.sub_task.download_finished.connect(self.__download_finished)
        self.sub_task.progress.connect(self.progress.emit)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task_thread.start()

    def __download_finished(self):
        sub_task_download = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.SEARCH_EMAILS
            ),
            None,
        )
        if sub_task_download:
            sub_task_download["state"] = state.COMPLETED
            sub_task_download["status"] = status.SUCCESS

        self.logger.info(logger.MAIL_SCRAPER_DOWNLOAD_EMAILS)
        self.set_message_on_the_statusbar(logger.MAIL_SCRAPER_DOWNLOAD_EMAILS)

        self.download_finished.emit()

        self.__quit_to_sub_task()
        self.__finished()

    def __finished(self):
        self.logger.info(logger.MAIL_SCRAPER_COMPLETED)
        self.set_message_on_the_statusbar(logger.MAIL_SCRAPER_COMPLETED)
        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

    def __quit_to_sub_task(self):
        if self.sub_task_thread is not None:
            self.sub_task_thread.quit()
            self.sub_task_thread.wait()
            self.sub_task_thread = None
        if self.sub_task is not None:
            self.sub_task = None

    def __destroyed_handler(self, _dict):
        if self.sub_task_thread is not None and self.sub_task_thread.isRunning():
            self.sub_task_thread.quit()
            self.sub_task_thread.wait()

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()
